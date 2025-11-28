CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT user_uid IF NOT EXISTS FOR (u:User) REQUIRE u.uid IS UNIQUE;
CREATE CONSTRAINT article_uid IF NOT EXISTS FOR (a:Article) REQUIRE a.uid IS UNIQUE;
CREATE CONSTRAINT tag_uid IF NOT EXISTS FOR (t:Tag) REQUIRE t.uid IS UNIQUE;
CREATE CONSTRAINT cat_uid IF NOT EXISTS FOR (c:Category) REQUIRE c.uid IS UNIQUE;

Creación de datos de prueba 
CREATE (u:User {uid: randomUUID(), name: 'Admin', email: 'admin@blog.com', created_at: datetime()});
