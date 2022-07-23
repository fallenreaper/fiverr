<?php
include_once 'db.php';
if(isset($_POST['submit']))
{    
     $jobname = $_POST['jobname'];
     $jobaddress = $_POST['jobaddress'];
     $joblead = $_POST['joblead'];
     $jobstart = $_POST['jobstart'];
     $jobend = $_POST['jobend'];
     $estimatedhours = $_POST['estimatedhours'];
     $screener = $_POST['screener'];  // Above stored in 1 var, not multiple.

     $excavator = $_POST['excavator'];
     $shear = $_POST['shear'];
     $loader = $_POST['loader'];

     $haulingcompany = $_POST['haulingcompany'];
     $estimatedloads = $_POST['estimatedloads'];
     $loaddestination = $_POST['loaddestination'];
     $haulingnotes = $_POST['haulingnotes'];

     $fuelprovider = $_POST['fuelprovider'];
     $fuelphonenumber = $_POST['fuelphonenumber'];
     $fuelnotes = $_POST['fuelnotes'];

     $crewlodging = $_POST['crewlodging'];
     $crewnotes = $_POST['crewnotes'];
     
     $sql = "INSERT INTO jobs (`name`, `address`, `lead`, `start`, `end`, `estimatedhours`, `screener`, `excavator`, `shear`, `loader`, `haulingcompany`, `estimatedloads`, `loaddestination`, `fuelnotes`, `crewlodging`, `crewnotes`, `haulingnotes`, `fuelprovider`, `fuelphonenumber`) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);";
     $stmt = $conn->prepare($sql);
     if ($stmt === false){ 
      die("Failed to prepare statement.");
     }
     $stmt->bind_param("sssssisssssisssssss", $jobname, $jobadress, $joblead, $jobstart, $jobend, $estimatedhours, $screener, $excavator, $shear, $loader, $haulingcompany, $estimatedloads, $loaddestination, $fuelnotes, $crewlodging, $crewnotes, $haulingnotes, $fuelprovider, $fuelphonenumber );
     $stmt->execute();
     
     mysqli_close($conn);
     echo "Added.";
}
?>