<?php
   $host        = "db"; # Service Name (Local DNS or IP)
   $port        = "3306";
   $dbname      = "jobdb";
   $user = "jobuser";
   $password = "password";
   global $conn;
   $conn = new mysqli($host, $user, $password, $dbname);
   
   if($conn->connect_error) {
      die("Connection Failed: ". $conn->connect_error);
   }
   ?>