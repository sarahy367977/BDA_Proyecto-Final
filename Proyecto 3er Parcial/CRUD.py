from neo4j import GraphDatabase
import uuid
from datetime import datetime

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Neo4j123")  

class BlogCompleto:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self._crear_constraints()

    def close(self):
        self.driver.close()

    def _crear_constraints(self):
        """Crea índices y restricciones para garantizar la integridad de los datos."""
        queries = [
            "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
            "CREATE CONSTRAINT user_uid IF NOT EXISTS FOR (u:User) REQUIRE u.uid IS UNIQUE",
            "CREATE CONSTRAINT article_uid IF NOT EXISTS FOR (a:Article) REQUIRE a.uid IS UNIQUE",
            "CREATE CONSTRAINT tag_uid IF NOT EXISTS FOR (t:Tag) REQUIRE t.uid IS UNIQUE",
            "CREATE CONSTRAINT cat_uid IF NOT EXISTS FOR (c:Category) REQUIRE c.uid IS UNIQUE",
            "CREATE CONSTRAINT comment_uid IF NOT EXISTS FOR (k:Comment) REQUIRE k.uid IS UNIQUE"
        ]
        with self.driver.session() as session:
            for q in queries:
                session.run(q)

    # USUARIOS
    def crear_usuario(self, nombre, email):
        uid = str(uuid.uuid4())
        query = """
        CREATE (u:User {uid: $uid, name: $name, email: $email, created_at: datetime()})
        RETURN u.uid as id
        """
        with self.driver.session() as session:
            result = session.run(query, uid=uid, name=nombre, email=email)
            return result.single()["id"]

    def obtener_usuarios(self):
        query = "MATCH (u:User) RETURN u.uid as _id, u.name as name, u.email as email"
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]

    def obtener_usuario_por_id(self, user_id):
        query = "MATCH (u:User {uid: $uid}) RETURN u.uid as _id, u.name as name, u.email as email"
        with self.driver.session() as session:
            result = session.run(query, uid=user_id).single()
            return dict(result) if result else None

    def actualizar_usuario(self, user_id, nuevos_datos):
        query = """
        MATCH (u:User {uid: $uid})
        SET u += $props
        """
        with self.driver.session() as session:
            session.run(query, uid=user_id, props=nuevos_datos)

    def eliminar_usuario(self, user_id):
        query = """
        MATCH (u:User {uid: $uid})
        OPTIONAL MATCH (u)-[:WROTE]->(c:Comment)
        OPTIONAL MATCH (u)-[:WROTE]->(a:Article)
        DETACH DELETE c
        DETACH DELETE a
        DETACH DELETE u
        """
        with self.driver.session() as session:
            session.run(query, uid=user_id)
    

    # ARTICULOS 
    def crear_articulo(self, titulo, texto, autor_id, tags=None, categorias=None):
        uid = str(uuid.uuid4())
        query = """
        MATCH (u:User {uid: $autor_id})
        CREATE (a:Article {uid: $uid, title: $title, text: $text, date: datetime()})
        MERGE (u)-[:WROTE]->(a)
        WITH a
        
        // Relacionar Tags (si existen)
        UNWIND $tags as tag_id
        MATCH (t:Tag {uid: tag_id})
        MERGE (a)-[:HAS_TAG]->(t)
        
        // Relacionar Categorias (si existen)
        WITH a
        UNWIND $cats as cat_id
        MATCH (c:Category {uid: cat_id})
        MERGE (a)-[:IN_CATEGORY]->(c)
        
        RETURN a.uid as id
        """
        tags = tags or []
        categorias = categorias or []
        
        with self.driver.session() as session:
            result = session.run(query, uid=uid, title=titulo, text=texto, autor_id=autor_id, tags=tags, cats=categorias)
            record = result.single()
            return record["id"] if record else None

    def obtener_articulos(self):
        query = "MATCH (a:Article) RETURN a.uid as _id, a.title as title"
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]
            
    def obtener_articulo_por_id(self, articulo_id):
        query = """
        MATCH (a:Article {uid: $uid})
        OPTIONAL MATCH (a)-[:HAS_TAG]->(t:Tag)
        OPTIONAL MATCH (a)-[:IN_CATEGORY]->(c:Category)
        OPTIONAL MATCH (u:User)-[:WROTE]->(a)
        RETURN a.uid as _id, a.title as title, a.text as text, u.uid as author_id,
               collect(t.uid) as tags, collect(c.uid) as categories
        """
        with self.driver.session() as session:
            result = session.run(query, uid=articulo_id).single()
            return dict(result) if result else None

    def obtener_articulos_con_autor(self):
        query = """
        MATCH (a:Article)<-[:WROTE]-(u:User)
        RETURN a.uid as _id, a.title as title, a.text as text, u.name as author_name
        """
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]

    def actualizar_articulo(self, articulo_id, nuevos_datos, tags_ids, cat_ids):
        query = """
        MATCH (a:Article {uid: $uid})
        SET a.title = $title, a.text = $text
        
        // Actualizar Autor
        WITH a
        MATCH (new_author:User {uid: $author_id})
        OPTIONAL MATCH (a)<-[r:WROTE]-(old_author)
        DELETE r
        MERGE (new_author)-[:WROTE]->(a)
        
        // Actualizar Tags (Borrar viejas, crear nuevas)
        WITH a
        OPTIONAL MATCH (a)-[r2:HAS_TAG]->()
        DELETE r2
        WITH a
        UNWIND $tags as tag_id
        MATCH (t:Tag {uid: tag_id})
        MERGE (a)-[:HAS_TAG]->(t)
        
        // Actualizar Categorias
        WITH a
        OPTIONAL MATCH (a)-[r3:IN_CATEGORY]->()
        DELETE r3
        WITH a
        UNWIND $cats as cat_id
        MATCH (c:Category {uid: cat_id})
        MERGE (a)-[:IN_CATEGORY]->(c)
        """
        with self.driver.session() as session:
            session.run(query, 
                        uid=articulo_id, 
                        title=nuevos_datos['title'], 
                        text=nuevos_datos['text'],
                        author_id=nuevos_datos['author_id'],
                        tags=tags_ids,
                        cats=cat_ids)

    def eliminar_articulo(self, articulo_id):
        query = "MATCH (a:Article {uid: $uid}) DETACH DELETE a"
        with self.driver.session() as session:
            session.run(query, uid=articulo_id)

    def crear_tag(self, nombre, url):
        uid = str(uuid.uuid4())
        query = "CREATE (t:Tag {uid: $uid, name: $name, url: $url}) RETURN t.uid"
        with self.driver.session() as session:
            session.run(query, uid=uid, name=nombre, url=url)

    def obtener_tags(self):
        query = "MATCH (t:Tag) RETURN t.uid as _id, t.name as name, t.url as url"
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]
            
    def obtener_tag_por_id(self, tag_id):
        query = "MATCH (t:Tag {uid: $uid}) RETURN t.uid as _id, t.name as name, t.url as url"
        with self.driver.session() as session:
            return dict(session.run(query, uid=tag_id).single() or {})

    def actualizar_tag(self, tag_id, nuevos_datos):
        query = "MATCH (t:Tag {uid: $uid}) SET t += $props"
        with self.driver.session() as session:
            session.run(query, uid=tag_id, props=nuevos_datos)

    def eliminar_tag(self, tag_id):
        with self.driver.session() as session:
            session.run("MATCH (t:Tag {uid: $uid}) DETACH DELETE t", uid=tag_id)

    def crear_categoria(self, nombre, url):
        uid = str(uuid.uuid4())
        query = "CREATE (c:Category {uid: $uid, name: $name, url: $url}) RETURN c.uid"
        with self.driver.session() as session:
            session.run(query, uid=uid, name=nombre, url=url)

    def obtener_categorias(self):
        query = "MATCH (c:Category) RETURN c.uid as _id, c.name as name, c.url as url"
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]
            
    def obtener_categoria_por_id(self, cat_id):
        query = "MATCH (c:Category {uid: $uid}) RETURN c.uid as _id, c.name as name, c.url as url"
        with self.driver.session() as session:
            return dict(session.run(query, uid=cat_id).single() or {})

    def actualizar_categoria(self, cat_id, nuevos_datos):
        query = "MATCH (c:Category {uid: $uid}) SET c += $props"
        with self.driver.session() as session:
            session.run(query, uid=cat_id, props=nuevos_datos)

    def eliminar_categoria(self, cat_id):
        with self.driver.session() as session:
            session.run("MATCH (c:Category {uid: $uid}) DETACH DELETE c", uid=cat_id)

    # COMENTARIOS 
    def crear_comentario(self, articulo_id, autor_id, texto):
        uid = str(uuid.uuid4())
        query = """
        MATCH (a:Article {uid: $aid}), (u:User {uid: $uid_user})
        CREATE (c:Comment {uid: $cid, text: $text, date: datetime()})
        MERGE (u)-[:WROTE]->(c)
        MERGE (c)-[:ON_ARTICLE]->(a)
        RETURN c.uid
        """
        with self.driver.session() as session:
            session.run(query, cid=uid, aid=articulo_id, uid_user=autor_id, text=texto)

    def obtener_comentarios(self):
        query = """
        MATCH (c:Comment)-[:ON_ARTICLE]->(a:Article)
        MATCH (c)<-[:WROTE]-(u:User)
        RETURN c.uid as _id, c.text as text, u.name as author_name, 
               a.title as article_title, u.uid as author_id, a.uid as article_id
        """
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]
            
    def obtener_comentario_por_id(self, com_id):
        query = """
        MATCH (c:Comment {uid: $uid})-[:ON_ARTICLE]->(a:Article)
        MATCH (c)<-[:WROTE]-(u:User)
        RETURN c.uid as _id, c.text as text, u.uid as author_id, a.uid as article_id
        """
        with self.driver.session() as session:
            result = session.run(query, uid=com_id).single()
            return dict(result) if result else None

    def actualizar_comentario(self, comentario_id, texto, autor_id, articulo_id):
        query = """
        MATCH (c:Comment {uid: $cid})
        SET c.text = $text
        // Rehacer relaciones si cambiaron
        WITH c
        MATCH (c)-[r1:ON_ARTICLE]->() DELETE r1
        MATCH (c)<-[r2:WROTE]-() DELETE r2
        WITH c
        MATCH (a:Article {uid: $aid})
        MATCH (u:User {uid: $uid_user})
        MERGE (c)-[:ON_ARTICLE]->(a)
        MERGE (u)-[:WROTE]->(c)
        """
        with self.driver.session() as session:
            session.run(query, cid=comentario_id, text=texto, uid_user=autor_id, aid=articulo_id)

    def eliminar_comentario(self, comentario_id):
        with self.driver.session() as session:
            session.run("MATCH (c:Comment {uid: $uid}) DETACH DELETE c", uid=comentario_id)