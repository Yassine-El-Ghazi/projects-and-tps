<?php
require 'db.php';  // Assuming db.php contains the PDO connection
require 'dashboard.php'; // Assuming dashboard.php contains necessary dashboard logic

// Fetch users from the database
$query = "SELECT * FROM Users ORDER BY username"; // Fetching users ordered by username
$stmt = $pdo->prepare($query);  // Use $pdo instead of $conn
$stmt->execute();
$users = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Users List - Library Management System</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 150px;
            min-height: 100vh;
            box-sizing: border-box;
            background-image: url("books.jpg");
            background-repeat: no-repeat;
            background-size: cover;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
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
        .add-btn {
            display: inline-block;
            padding: 12px 24px;
            background-color: #DF9755;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            margin-bottom: 20px;
            transition: background-color 0.3s ease;
        }
        .add-btn:hover {
            background-color: #357abd;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: white;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background-color: #f8f9fa;
            color: #2c3e50;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .action-btn {
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            color: white;
            font-weight: bold;
            margin-right: 8px;
            display: inline-block;
        }
        .edit-btn {
            background-color: #f39c12;
        }
        .edit-btn:hover {
            background-color: #d68910;
        }
        .delete-btn {
            background-color: #e74c3c;
        }
        .delete-btn:hover {
            background-color: #c0392b;
        }
        .success-message {
            background-color: #2ecc71;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Users Management</h1>

    <!-- Optionally display a success message -->
    <?php
    if (isset($_GET['success'])) {
        switch ($_GET['success']) {
            case 'added':
                echo "<div class='success-message'>User successfully added!</div>";
                break;
            case 'modified':
                echo "<div class='success-message'>User successfully updated!</div>";
                break;
            case 'deleted':
                echo "<div class='success-message'>User successfully deleted!</div>";
                break;
        }
    }
    ?>

    <a href="add_user.php" class="add-btn">Add New User</a>

    <table>
        <thead>
        <tr>
            <th>Name</th>
            <th>Password (Hidden)</th> <!-- Hide the password -->
            <th>Role</th>
            <th>Actions</th>
        </tr>
        </thead>
        <tbody>
        <?php foreach ($users as $user): ?>
            <tr>
                <td><?php echo htmlspecialchars($user['username']); ?></td>
                <td><?php echo htmlspecialchars(MD5($user['username'])); ?></td>
                <td><?php echo htmlspecialchars($user['role']); ?></td>
                <td>
                    <a href="modi_users.php?id=<?php echo $user['id']; ?>" class="action-btn edit-btn">Modify</a>
                    <a href="deleteusers.php?id=<?php echo $user['id']; ?>" class="action-btn delete-btn" onclick="return confirm('Are you sure you want to delete this user?')">Delete</a>
                </td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
</body>
</html>
