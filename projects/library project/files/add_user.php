<?php

require 'db.php';
$message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['add_user'])) {
    $username = $_POST['username'];
    $password = MD5($_POST['password']); // Sécuriser le mot de passe
    $role = $_POST['role'];

    try {
        $query = "INSERT INTO Users (username, password, role) VALUES (:username, :password, :role)";
        $stmt = $pdo->prepare($query);
        $stmt->bindParam(':username', $username);
        $stmt->bindParam(':password', $password);
        $stmt->bindParam(':role', $role);

        if ($stmt->execute()) {
            header("Location: user_dis.php?success=added");
            exit();
        } else {
            $message = "Error adding user.";
        }
    } catch (PDOException $e) {
        $message = "Error: " . $e->getMessage();
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add User - User Management System</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
            box-sizing: border-box;
            color: #333;
            background-image: url("books.jpg");
            background-repeat: no-repeat;
            background-size: cover;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
        }

        p {
            color: #2ecc71;
            font-size: 16px;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
            font-weight: bold;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: bold;
        }

        .form-control {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
            box-sizing: border-box;
        }

        .form-control:focus {
            border-color: #4a90e2;
            outline: none;
        }

        select.form-control {
            background-color: white;
        }

        .btn {
            display: inline-block;
            width: 100%;
            padding: 12px;
            background-color: #DF9755;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .btn:hover {
            background-color: #285e8e;
        }

        .error {
            color: #e74c3c;
            text-align: center;
            margin-top: 10px;
        }

        .back-link {
            display: block;
            margin-top: 20px;
            text-align: center;
            color: #DF9755;
            text-decoration: none;
        }

        .back-link:hover {
            color: #DF9755;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Add User</h1>

    <?php if (!empty($message)): ?>
        <p><?php echo htmlspecialchars($message); ?></p>
    <?php endif; ?>

    <form method="POST" action="">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" class="form-control" required>
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" class="form-control" required>
        </div>
        <div class="form-group">
            <label for="role">Role</label>
            <select id="role" name="role" class="form-control" required>
                <option value="member">Member</option>
                <option value="admin">Administrator</option>
            </select>
        </div>
        <button type="submit" name="add_user" class="btn">Add User</button>
    </form>

    <a href="user_dis.php" class="back-link">Back to User Management</a>
</div>
</body>
</html>


