<?php
  include_once 'db.php';
  // If you want to add complete where clauses, you would either want to add them here or filter the resulting $arr
  $result = $conn->query("select `id`, `name`, `address`, `lead`, `start`, `end`, `estimatedhours`, `screener`, `excavator`, `shear`, `loader`, `haulingcompany`, `estimatedloads`, `loaddestination`, `haulingnotes`, `crewlodging`, `crewnotes`, `fuelprovider`, `fuelphonenumber`, `fuelnotes` from jobs;");
  $arr = $result->fetch_all();
  // These are just header strings.  They can be changed around for human readability.
  $headers = array("id", "name", "address", "lead", "start date", "end date", "estimated hours", "screener", "excavator", "shear", "loader", "hauling company", "estimated loads", "load destination", "hauling notes" , "crew lodging", "crew notes","fuel provider", "fuel phone numner", "fuel notes");

  // if you want to add buttons to accomplish different tasks, the 'id' property will be the prop you want to leverage for deleting.
  // If you want to filter, you can do that in the front end with the full list, or edit the query above, or edit the resulting arr.
  // if you want to sort the data, ( by default it is asc by id ) you just need to add a order by clause to the query command.

  // I left the CSS bland because I dont know your color scheme and design, but this will do a list and you can change styles as you see fit.
?>

<html>
  <head>
    <style>
      div{
        border: solid 1px black;
      }
      .table {
        display: table;
      }
      .row, .rowheader {
        display: table-row;
      }
      .cell {
        display: table-cell;
      }
    </style>
  </head>
  <body>

    <div class="table">
      <div class="rowheader">
        <?php foreach( $headers as $s) { ?>
          <div class="cell"><?=$s; ?></div>
        <?php } ?>
      </div>
      <?php foreach( $arr as $row) {?>
      <div class="row">
        <?php foreach($row as $key => $value) { ?>
        <div class="cell"><?=$value; ?></div>
        <?php } ?>
      </div>
      <?php } ?>
    </div>

  </body>
</html>