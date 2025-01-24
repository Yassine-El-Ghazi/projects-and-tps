<?php
// Include the database connection file
require 'db.php'; // Assuming db.php is in the same directory
require 'dashboard.php';
// Fetching all books from the database
try {
    // SQL query to fetch books ordered by title
    $query = "SELECT * FROM Books ORDER BY title";
    $stmt = $pdo->prepare($query); // Prepare the SQL statement
    $stmt->execute(); // Execute the statement
    $books = $stmt->fetchAll(PDO::FETCH_ASSOC); // Fetch all books as an associative array
} catch (PDOException $e) {
    // Handle the exception if the query fails
    die("Error fetching books: " . $e->getMessage());
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Books List - Library Management System</title>
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
    <h1>Books Management</h1>

    <?php
    // Display success message if there is any
    if (isset($_GET['success'])) {
        switch ($_GET['success']) {
            case 'added':
                echo "<div class='success-message'>Book successfully added!</div>";
                break;
            case 'modified':
                echo "<div class='success-message'>Book successfully updated!</div>";
                break;
            case 'deleted':
                echo "<div class='success-message'>Book successfully deleted!</div>";
                break;
        }
    }
    ?>

    <a href="addbooks.php" class="add-btn">Add New Book</a>

    <table>
        <thead>
        <tr>
            <th>Title</th>
            <th>Author</th>
            <th>Genre</th>
            <th>Publication Date</th>
            <th>Available Copies</th>
            <th>Actions</th>
        </tr>
        </thead>
        <tbody>
        <?php foreach ($books as $book): ?>
            <tr>
                <td><?php echo htmlspecialchars($book['title']); ?></td>
                <td><?php echo htmlspecialchars($book['author']); ?></td>
                <td><?php echo htmlspecialchars($book['genre']); ?></td>
                <td><?php echo date('Y-m-d', strtotime($book['publication_date'])); ?></td>
                <td><?php echo htmlspecialchars($book['number_of_books']); ?></td>
                <td>
                    <a href="modifybooks.php?id=<?php echo $book['id']; ?>" class="action-btn edit-btn">Modify</a>
                    <a href="deletebooks.php?delete_id=<?php echo $book['id']; ?>" class="action-btn delete-btn" onclick="return confirm('Are you sure you want to delete this book?')">Delete</a>
                </td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
</body>
</html>
