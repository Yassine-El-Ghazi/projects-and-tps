<?php
session_start();
require_once 'db.php'; // This will automatically include the $pdo connection

$message = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username']);
    $password = $_POST['password'];
    
    if (empty($username) || empty($password)) {
        $message = "Please fill in all fields.";
    } else {
        try {
            // Use the global $pdo object from db.php
            global $pdo;

            // Check if username exists
            $stmt = $pdo->prepare("SELECT id,password, role FROM Users WHERE username = ?");
            $stmt->execute([$username]);
            $user = $stmt->fetch();

            if ($user && md5($password) === $user['password']) {
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['role'] = $user['role'];
                $_SESSION['username'] = $username;
                $_SESSION["logged_in"] = "yes";
                header("Location: " . ($user['role'] === 'administrator' ? 'admin_page.php' : 'member_page.php'));
                exit;
            } else {
                $message = "Invalid username or password.";
            }
        } catch (PDOException $e) {
            $message = "An error occurred. Please try again later.";
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Library Management System - Login</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            background-image: url("library page.jpg");
            background-repeat: no-repeat;
            background-size: cover;


        }
        .container {
            background: #ffffff;
            max-width: 800px;
            width: 90%;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            display: flex;
            gap: 40px;
            align-items: center;
        }
        .login-title {
            font-size: 32px;
            font-weight: bold;
            color: #EB5A3C;
            margin-bottom: 30px;
            text-align: center;
        }
        .data {
            width: 100%;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .data:focus {
            border-color: #4a90e2;
            outline: none;
        }
        .submit {
            width: 100%;
            padding: 14px;
            background-color: #DF9755;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .submit:hover {
            background-color: #357abd;
        }
        .error {
            color: #e74c3c;
            font-size: 14px;
            margin-top: 10px;
            text-align: center;
        }
        .login-container {
            flex: 1;
        }
        .next-image {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .next-image img {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
        }
        a {
            color: #DF9755;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        a:hover {
            color: #DF9755;
        }
        p {
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="next-image">
        <img src="glasses-1052010_640.jpg" alt="Library Interior" />
    </div>
    <div class="login-container">
        <h1 class="login-title">Library Management System</h1>
        <form action="" method="POST">
            <input type="text" id="username" name="username" class="data" placeholder="Username" required>
            <input type="password" id="password" name="password" class="data" placeholder="Password" required>
            <button type="submit" class="submit">Login</button>
            <p>Don't have an account? <a href="signup.php">Register</a></p>
        </form>
        <?php if (!empty($message)): ?>
            <p class="error"><?= htmlspecialchars($message) ?></p>
        <?php endif; ?>
    </div>
</div>
</body>
</html>

