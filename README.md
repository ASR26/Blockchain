<h1>Descripción</h1>
  <p>Este proyecto consiste en replicar el funcionamiento de una <a href="https://es.wikipedia.org/wiki/Cadena_de_bloques">blockchain</a>, para ello se ha usado Python.</p>
  <p>El proceso de minado consiste en buscar un hash que concatenado al hash del bloque anterior cumpla una prueba predefinida, en este caso que comience con 'n' ceros, cada bloque debe ser más complejo que el anterior, para ello se ha implementado una dificultad que escalará en proporción al índice del bloque que se está minando</p>
<h1>Funcionamiento</h1>
   <p>El funcionamiento de la aplicación es muy simple, primero tendremos que ejecutar el programa usando python3</p>
   <code>python3 blockchain.py </code>
  <h2>Servidor</h2>
    <p>Una vez el servidor esté funcionando podremos acceder a el desde nuestro navegador accediendo a la url localhost:5000 (el puerto se puede cambiar en la línea 258)</p>
    <p>Nuestro servidor tendrá 2 páginas principales:</p>
    <ul>
      <li><code>/chain : Esta página nos mostrará la cadena completa, con todos los bloques que la componen</code></li>
      <li><code>/mine : Esta página minará un nuevo bloque con todas las transacciones que correspondan y lo añadirá a la cadena</code></li>
    </ul>
  <h2>Transacciones</h2>
    <p>Para realizar las transacciones tendremos que hacer una petición al servidor desde consola con le método POST, la cual tendrá los datos de la transacción en formato JSON. Un ejemplo de petición sería el siguiente:</p>
    <p><pre>$ curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "d4ee26eee15148ee92c6cd394edd974e",
 "recipient": "someone-other-address",
 "amount": 5
}' "http://localhost:5000/transactions/new"</pre></p>
