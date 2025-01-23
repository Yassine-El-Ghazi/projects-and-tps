<?php
session_start();
session_unset();
session_destroy();
header("Location: member_page.php");
exit();
?>

