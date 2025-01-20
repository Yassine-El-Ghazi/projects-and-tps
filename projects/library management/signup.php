<?php
require_once 'db.php'; // This will automatically include the $pdo connection
session_start();

if (isset($_SESSION['user_id'])) {
    header("Location: member_page.php");
    exit();
}

$message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST['username']);
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];

    if (empty($username) || empty($password) || empty($confirm_password)) {
        $message = "Please fill in all fields.";
    } elseif ($password !== $confirm_password) {
        $message = "Passwords do not match!";
    } else {
        try {
            // Use the global $pdo object from db.php
            global $pdo;

            // Check if username exists
            $stmt = $pdo->prepare("SELECT id FROM Users WHERE username = ?");
            $stmt->execute([$username]);
            
            if ($stmt->rowCount() > 0) {
                $message = "Username already exists!";
            } else {
                // Insert new user with md5 password hashing
                $hashed_password = md5($password);
                $stmt = $pdo->prepare("INSERT INTO Users (username, password, role) VALUES (?, ?, 'member')");
                
                if ($stmt->execute([$username, $hashed_password])) {
                    $_SESSION['registration_success'] = true;
                    header("Location: projectlogin.php");
                    exit();
                } else {
                    $message = "Registration failed!";
                }
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
    <title>Register - Library Management System</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-image: url("library page.jpg");
            background-repeat: no-repeat;
            background-size: cover;

        }
        .container {
            background: #ffffff;
            max-width: 500px;
            width: 90%;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }
        .signup-title {
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
            box-sizing: border-box;
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
        p {
            text-align: center;
            margin-top: 20px;
        }
        a {
            color: #DF9755;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        a:hover {
            color: #DF9755;
        }
    </style>
</head>
<body>
<div class="container">
    <h1 class="signup-title">Create Account</h1>
    <form action="" method="POST">
        <input type="text" name="username" class="data" placeholder="Username" required 
               minlength="3" maxlength="50" pattern="[A-Za-z0-9_]+" 
               title="Username can only contain letters, numbers, and underscore">
        <input type="password" name="password" class="data" placeholder="Password" required minlength="6">
        <input type="password" name="confirm_password" class="data" placeholder="Confirm Password" required>
        <button type="submit" class="submit">Register</button>
        <p>Already have an account? <a href="projectlogin.php">Login</a></p>
    </form>
    <?php if (!empty($message)): ?>
        <p class='error'><?= htmlspecialchars($message) ?></p>
    <?php endif; ?>
</div>
</body>
</html>

