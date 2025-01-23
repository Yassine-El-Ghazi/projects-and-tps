<?php
session_start();
if (!isset($_SESSION["logged_in"]) || $_SESSION["logged_in"] != "yes") {
    header("Location: index.php");
    exit();
}

$dsn = 'mysql:host=localhost;dbname=LibraryManagement';
$username = 'root';
$password = '';

try {
    $conn = new PDO($dsn, $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}

$message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $title = $_POST['title'];
    $author = $_POST['author'];
    $genre = $_POST['genre'];
    $publication_date = $_POST['publication_date'];
    $number_of_books = $_POST['number_of_books'];

    try {
        $query = "INSERT INTO Books (title, author, genre, publication_date, number_of_books) 
                  VALUES (:title, :author, :genre, :publication_date, :number_of_books)";
        $stmt = $conn->prepare($query);
        $stmt->bindParam(':title', $title);
        $stmt->bindParam(':author', $author);
        $stmt->bindParam(':genre', $genre);
        $stmt->bindParam(':publication_date', $publication_date);
        $stmt->bindParam(':number_of_books', $number_of_books);

        if ($stmt->execute()) {
            header("Location: displaybooks.php?success=added");
            exit();
        } else {
            $message = "Error adding book!";
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
    <title>Add New Book - Library Management System</title>
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
    <h1>Add New Book</h1>
    <form action="" method="POST">
        <div class="form-group">
            <label for="title">Book Title</label>
            <input type="text" id="title" name="title" class="form-control" required>
        </div>

        <div class="form-group">
            <label for="author">Author</label>
            <input type="text" id="author" name="author" class="form-control" required>
        </div>

        <div class="form-group">
            <label for="genre">Genre</label>
            <select id="genre" name="genre" class="form-control" required>
                <option value="">Select Genre</option>
                <option value="Romance">Romance</option>
                <option value="Science Fiction">Science Fiction</option>
                <option value="Action">Action</option>
                <option value="Mystery">Mystery</option>
                <option value="Fantasy">Fantasy</option>
                <option value="Horror">Horror</option>
                <option value="Biography">Biography</option>
                <option value="History">History</option>
                <option value="Children">Children</option>
                <option value="Young Adult">Young Adult</option>
            </select>
        </div>

        <div class="form-group">
            <label for="publication_date">Publication Date</label>
            <input type="date" id="publication_date" name="publication_date" class="form-control" required>
        </div>

        <div class="form-group">
            <label for="number_of_books">Number of Copies</label>
            <input type="number" id="number_of_books" name="number_of_books" min="1" class="form-control" required>
        </div>

        <div class="btn-container">
            <button type="submit" class="btn">Add Book</button>
        </div>
    </form>
    <?php
    if (!empty($message)) {
        echo "<p class='error'>$message</p>";
    }
    ?>
    <a href="displaybooks.php" class="back-link">Back to Books List</a>
</div>
</body>
</html>