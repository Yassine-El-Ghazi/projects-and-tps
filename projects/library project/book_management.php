<?php

session_start();
if (!isset($_SESSION["logged_in"]) || $_SESSION["logged_in"] != "yes") {
    header("Location: member_page.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Management - Library Management System</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-image: url("books.jpg");
            background-repeat: no-repeat;
            background-size: cover;
        }
        .dashboard {
            width: 100%;
            max-width: 1200px;
            background-color: #ffffff;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 40px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            color: #2c3e50;
            font-size: 36px;
            margin-bottom: 10px;
        }
        .menu-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
            justify-content: center;
        }
        .menu-item {
            background: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .menu-item:hover {
            transform: translateY(-8px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        }
        .menu-item h2 {
            color: #34495e;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .menu-item p {
            color: #7f8c8d;
            margin-bottom: 25px;
            font-size: 16px;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #DF9755;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: background-color 0.3s ease;
            font-size: 16px;
        }
        .button:hover {
            background-color: #3498db;
        }
    </style>
</head>
<body>
<div class="dashboard">
    <div class="header">
        <h1>Library Management</h1>
    </div>
    <div class="menu-container">
        <div class="menu-item">
            <h2>Books Management</h2>
            <p>View and add new ones to the library catalog</p>
            <a href="displaybooks.php" class="button"> Books</a>
        </div>
        <div class="menu-item">
            <h2>Statistics</h2>
            <p>View statistique.</p>
            <a href="staticadmin.php" class="button">Statistics</a>
        </div>
    </div>
</div>
</body>
</html>
