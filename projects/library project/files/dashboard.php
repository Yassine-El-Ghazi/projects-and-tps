

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $pageTitle ?? 'Library Management System'; ?></title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }

        .navbar {
            background-color: #DF9755;
            padding: 10px 0;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }

        .navbar .menu {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .navbar .menu button {
            padding: 15px 25px;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
            background-color: #DF9755;
            color: white;
            margin: 0 10px;
        }

        .navbar .menu button:hover {
            background-color: cornflowerblue;
        }

        .navbar .logout {
            position: absolute;
            right: 20px;
            top: 10px;
            background-color: #e74c3c;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }

        .navbar .logout:hover {
            background-color: #c0392b;
        }

        .container {
            max-width: 800px;
            margin: 80px auto 20px; /* Adjusted margin to account for fixed navbar */
            background: #fff;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }

        h1 {
            color: #6a1b9a;
            text-align: center;
            font-size: 36px;
        }
    </style>
</head>
<body>
<div class="navbar">
    <div class="menu">
        <button onclick="window.location.href='book_management.php'">Manage Books</button>
        <button onclick="window.location.href='user_dis.php'">Manage Users</button>
    </div>
    <button class="logout" onclick="window.location.href='logout.php'">Go to user Page</button>
</div>
</body>
</html>