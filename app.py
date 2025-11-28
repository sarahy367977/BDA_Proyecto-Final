from flask import Flask, render_template, request, redirect, url_for
from CRUD import BlogCompleto   

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
blog = BlogCompleto() 

@app.route('/')
def index():
    return redirect(url_for('pagina_usuarios'))

@app.route('/usuarios')
def pagina_usuarios():
    lista_usuarios = blog.obtener_usuarios()
    return render_template('usuarios.html', usuarios=lista_usuarios)

@app.route('/articulos')
def pagina_articulos():
    autores = blog.obtener_usuarios()
    tags = blog.obtener_tags()
    categorias = blog.obtener_categorias()
    lista_articulos = blog.obtener_articulos_con_autor()
    return render_template('articulos.html', articulos=lista_articulos, autores=autores, tags=tags, categorias=categorias)

@app.route('/tags')
def pagina_tags():
    tags = blog.obtener_tags()
    categorias = blog.obtener_categorias()
    return render_template('tags.html', tags=tags, categorias=categorias)

@app.route('/comentarios')
def pagina_comentarios():
    autores = blog.obtener_usuarios()
    articulos = blog.obtener_articulos() 
    lista_comentarios = blog.obtener_comentarios()

    return render_template('comentarios.html', comentarios=lista_comentarios, autores=autores, articulos=articulos)

@app.route('/usuarios/crear', methods=['POST'])
def crear_usuario():
    if request.method == 'POST':
        blog.crear_usuario(request.form['nombre'], request.form['email'])
    return redirect(url_for('pagina_usuarios'))

@app.route('/articulos/crear', methods=['POST'])
def crear_articulo():
    if request.method == 'POST':
        blog.crear_articulo(request.form['titulo'], 
                            request.form['texto'], 
                            request.form['autor_id'], 
                            tags=request.form.getlist('tags'), 
                            categorias=request.form.getlist('categorias'))
    return redirect(url_for('pagina_articulos'))

@app.route('/tags/crear-tag', methods=['POST'])
def crear_tag():
    if request.method == 'POST':
        blog.crear_tag(request.form['nombre_tag'], request.form['url_tag'])
    return redirect(url_for('pagina_tags'))

@app.route('/tags/crear-categoria', methods=['POST'])
def crear_categoria():
    if request.method == 'POST':
        blog.crear_categoria(request.form['nombre_cat'], request.form['url_cat'])
    return redirect(url_for('pagina_tags'))

@app.route('/comentarios/crear', methods=['POST'])
def crear_comentario():
    if request.method == 'POST':
        blog.crear_comentario(request.form['articulo_id'], 
                             request.form['autor_id'], 
                             request.form['texto'])
    return redirect(url_for('pagina_comentarios'))

@app.route('/usuarios/eliminar/<user_id>')
def eliminar_usuario(user_id):
    blog.eliminar_usuario(user_id)
    return redirect(url_for('pagina_usuarios'))

@app.route('/articulos/eliminar/<articulo_id>')
def eliminar_articulo(articulo_id):
    blog.eliminar_articulo(articulo_id)
    return redirect(url_for('pagina_articulos'))

@app.route('/tags/eliminar-tag/<tag_id>')
def eliminar_tag(tag_id):
    blog.eliminar_tag(tag_id)
    return redirect(url_for('pagina_tags'))

@app.route('/tags/eliminar-categoria/<categoria_id>')
def eliminar_categoria(categoria_id):
    blog.eliminar_categoria(categoria_id)
    return redirect(url_for('pagina_tags'))

@app.route('/comentarios/eliminar/<comentario_id>')
def eliminar_comentario(comentario_id):
    blog.eliminar_comentario(comentario_id)
    return redirect(url_for('pagina_comentarios'))

@app.route('/usuarios/editar/<user_id>')
def pagina_editar_usuario(user_id):
    usuario = blog.obtener_usuario_por_id(user_id) 
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/articulos/editar/<articulo_id>')
def pagina_editar_articulo(articulo_id):
    articulo = blog.obtener_articulo_por_id(articulo_id) 
    autores = blog.obtener_usuarios()
    tags = blog.obtener_tags()
    categorias = blog.obtener_categorias()
    
    return render_template('editar_articulo.html', 
                           articulo=articulo, 
                           autores=autores, 
                           tags=tags, 
                           categorias=categorias)

@app.route('/tags/editar-tag/<tag_id>')
def pagina_editar_tag(tag_id):
    tag = blog.obtener_tag_por_id(tag_id) 
    return render_template('editar_tag.html', tag=tag)

@app.route('/tags/editar-categoria/<categoria_id>')
def pagina_editar_categoria(categoria_id):
    categoria = blog.obtener_categoria_por_id(categoria_id) 
    return render_template('editar_categoria.html', categoria=categoria)

@app.route('/comentarios/editar/<comentario_id>')
def pagina_editar_comentario(comentario_id):
    comentario = blog.obtener_comentario_por_id(comentario_id) 
    autores = blog.obtener_usuarios()
    articulos = blog.obtener_articulos()
    
    return render_template('editar_comentario.html', 
                           comentario=comentario, 
                           autores=autores, 
                           articulos=articulos)

@app.route('/usuarios/actualizar/<user_id>', methods=['POST'])
def actualizar_usuario_accion(user_id):
    if request.method == 'POST':
        nuevos_datos = {
            "name": request.form['nombre'],
            "email": request.form['email']
        }
        blog.actualizar_usuario(user_id, nuevos_datos)
    return redirect(url_for('pagina_usuarios'))

@app.route('/articulos/actualizar/<articulo_id>', methods=['POST'])
def actualizar_articulo_accion(articulo_id):
    if request.method == 'POST':
        nuevos_datos = {
            "title": request.form['titulo'],
            "text": request.form['texto'],
            "author_id": request.form['autor_id'] 
        }
        tags_ids = request.form.getlist('tags')
        cat_ids = request.form.getlist('categorias')
        
        blog.actualizar_articulo(articulo_id, nuevos_datos, tags_ids, cat_ids)
    return redirect(url_for('pagina_articulos'))

@app.route('/tags/actualizar-tag/<tag_id>', methods=['POST'])
def actualizar_tag_accion(tag_id):
    if request.method == 'POST':
        nuevos_datos = { "name": request.form['nombre_tag'], "url": request.form['url_tag'] }
        blog.actualizar_tag(tag_id, nuevos_datos)
    return redirect(url_for('pagina_tags'))

@app.route('/tags/actualizar-categoria/<categoria_id>', methods=['POST'])
def actualizar_categoria_accion(categoria_id):
    if request.method == 'POST':
        nuevos_datos = { "name": request.form['nombre_cat'], "url": request.form['url_cat'] }
        blog.actualizar_categoria(categoria_id, nuevos_datos)
    return redirect(url_for('pagina_tags'))

@app.route('/comentarios/actualizar/<comentario_id>', methods=['POST'])
def actualizar_comentario_accion(comentario_id):
    if request.method == 'POST':
        blog.actualizar_comentario(
            comentario_id, 
            request.form['texto'],
            request.form['autor_id'],
            request.form['articulo_id']
        )
    return redirect(url_for('pagina_comentarios'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)