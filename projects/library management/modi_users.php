<?php

require 'db.php';
require'dashboard.php';
$message = "";
$user = null;

// Fetch user details if ID is provided
if (isset($_GET['id'])) {
    $id = $_GET['id'];
    try {
        $query = "SELECT * FROM Users WHERE id = :id";
        $stmt = $pdo->prepare($query);
        $stmt->bindParam(':id', $id);
        $stmt->execute();
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$user) {
            header("Location: displayusers.php");
            exit();
        }
    } catch (PDOException $e) {
        $message = "Error: " . $e->getMessage();
    }
}

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_user'])) {
    $id = $_POST['id'];
    $username = $_POST['username'];
    $password = MD5($_POST['password']); // Hashing password
    $role = $_POST['role'];

    try {
        $query = "UPDATE Users SET 
                  username = :username, 
                  password = :password, 
                  role = :role
                  WHERE id = :id";

        $stmt = $pdo->prepare($query);
        $stmt->bindParam(':id', $id);
        $stmt->bindParam(':username', $username);
        $stmt->bindParam(':password', $password);
        $stmt->bindParam(':role', $role);

        if ($stmt->execute()) {
            header("Location:user_dis.php");
            exit();
        } else {
            $message = "Error updating user.";
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
    <title>Modify User - User Management System</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
            box-sizing: border-box;
            background-image: url("books.jpg");
            background-repeat: no-repeat;
            background-size: cover;

        }
        .container {
            max-width: 800px;
            margin: 5 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
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
            border: 2px solid #e0e0e0;
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
            padding: 12px 24px;
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
            background-color: #357abd;
        }
        .btn-container {
            text-align: center;
            margin-top: 30px;
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
            color: #357abd;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Modify User</h1>

    <?php if (!empty($message)): ?>
        <p class="error"><?php echo $message; ?></p>
    <?php endif; ?>

    <?php if ($user): ?>
        <form method="POST" action="">
            <input type="hidden" name="id" value="<?php echo htmlspecialchars($user['id']); ?>">

            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" class="form-control"
                       value="<?php echo htmlspecialchars($user['username']); ?>" required>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" class="form-control" required>
            </div>

            <div class="form-group">
                <label for="role">Role</label>
                <select id="role" name="role" class="form-control" required>
                    <option value="member" <?php echo ($user['role'] == 'member') ? 'selected' : ''; ?>>Member</option>
                    <option value="administrator" <?php echo ($user['role'] == 'administrator') ? 'selected' : ''; ?>>Administrator</option>
                </select>
            </div>

            <div class="btn-container">
                <button type="submit" name="update_user" class="btn">Update User</button>
            </div>
        </form>
    <?php endif; ?>

    <a href="user_dis.php" class="back-link">Back to Users List</a>
</div>
</body>
</html>

