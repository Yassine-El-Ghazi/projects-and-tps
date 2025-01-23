<?php
require 'db.php';

$message = "";
$book = null;

// Fetch book details if ID is provided
if (isset($_GET['id'])) {
    $id = $_GET['id'];
    try {
        $query = "SELECT * FROM Books WHERE id = :id";
        $stmt = $pdo->prepare($query);
        $stmt->bindParam(':id', $id, PDO::PARAM_INT);
        $stmt->execute();
        $book = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$book) {
            // If no book found, redirect to books list with an error message
            header("Location: displaybooks.php?error=book_not_found");
            exit();
        }
    } catch (PDOException $e) {
        $message = "Error fetching book details: " . $e->getMessage();
    }
}

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_book'])) {
    $id = $_POST['id'];
    $title = trim($_POST['title']);
    $author = trim($_POST['author']);
    $genre = $_POST['genre'];
    $publication_date = $_POST['publication_date'];
    $number_of_books = (int)$_POST['number_of_books'];

    if (empty($title) || empty($author) || empty($genre) || empty($publication_date)) {
        $message = "All fields are required.";
    } else {
        try {
            $query = "UPDATE Books SET 
                      title = :title, 
                      author = :author, 
                      genre = :genre, 
                      publication_date = :publication_date, 
                      number_of_books = :number_of_books 
                      WHERE id = :id";

            $stmt = $pdo->prepare($query);
            $stmt->bindParam(':id', $id, PDO::PARAM_INT);
            $stmt->bindParam(':title', $title);
            $stmt->bindParam(':author', $author);
            $stmt->bindParam(':genre', $genre);
            $stmt->bindParam(':publication_date', $publication_date);
            $stmt->bindParam(':number_of_books', $number_of_books, PDO::PARAM_INT);

            if ($stmt->execute()) {
                header("Location: displaybooks.php?success=modified");
                exit();
            } else {
                $message = "Error updating book. Please try again.";
            }
        } catch (PDOException $e) {
            $message = "Error: " . $e->getMessage();
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modify Book - Library Management System</title>
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
    <h1>Modify Book</h1>

    <?php if (!empty($message)): ?>
        <p class="error"><?php echo htmlspecialchars($message); ?></p>
    <?php endif; ?>

    <?php if ($book): ?>
        <form method="POST" action="">
            <input type="hidden" name="id" value="<?php echo htmlspecialchars($book['id']); ?>">

            <div class="form-group">
                <label for="title">Book Title</label>
                <input type="text" id="title" name="title" class="form-control"
                       value="<?php echo htmlspecialchars($book['title']); ?>" required>
            </div>

            <div class="form-group">
                <label for="author">Author</label>
                <input type="text" id="author" name="author" class="form-control"
                       value="<?php echo htmlspecialchars($book['author']); ?>" required>
            </div>

            <div class="form-group">
                <label for="genre">Genre</label>
                <select id="genre" name="genre" class="form-control" required>
                    <option value="Romance" <?php echo ($book['genre'] == 'Romance') ? 'selected' : ''; ?>>Romance</option>
                    <option value="Science Fiction" <?php echo ($book['genre'] == 'Science Fiction') ? 'selected' : ''; ?>>Science Fiction</option>
                    <option value="Action" <?php echo ($book['genre'] == 'Action') ? 'selected' : ''; ?>>Action</option>
                    <option value="Mystery" <?php echo ($book['genre'] == 'Mystery') ? 'selected' : ''; ?>>Mystery</option>
                    <option value="Fantasy" <?php echo ($book['genre'] == 'Fantasy') ? 'selected' : ''; ?>>Fantasy</option>
                    <option value="Horror" <?php echo ($book['genre'] == 'Horror') ? 'selected' : ''; ?>>Horror</option>
                    <option value="Biography" <?php echo ($book['genre'] == 'Biography') ? 'selected' : ''; ?>>Biography</option>
                    <option value="History" <?php echo ($book['genre'] == 'History') ? 'selected' : ''; ?>>History</option>
                    <option value="Children" <?php echo ($book['genre'] == 'Children') ? 'selected' : ''; ?>>Children</option>
                    <option value="Young Adult" <?php echo ($book['genre'] == 'Young Adult') ? 'selected' : ''; ?>>Young Adult</option>
                </select>
            </div>

            <div class="form-group">
                <label for="publication_date">Publication Date</label>
                <input type="date" id="publication_date" name="publication_date" class="form-control"
                       value="<?php echo htmlspecialchars($book['publication_date']); ?>" required>
            </div>

            <div class="form-group">
                <label for="number_of_books">Number of Copies</label>
                <input type="number" id="number_of_books" name="number_of_books" class="form-control"
                       value="<?php echo htmlspecialchars($book['number_of_books']); ?>" min="0" required>
            </div>

            <div class="btn-container">
                <button type="submit" name="update_book" class="btn">Update Book</button>
            </div>
        </form>
    <?php endif; ?>

    <a href="displaybooks.php" class="back-link">Back to Books List</a>
</div>
</body>
</html>
