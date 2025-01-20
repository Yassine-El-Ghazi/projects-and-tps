<?php
require 'db.php'; // Include database connection file

// Check if the 'delete_id' is passed in the URL
if (isset($_GET['delete_id'])) {
    $book_id = $_GET['delete_id'];

    // Check if the book exists in the database
    $checkStmt = $pdo->prepare("SELECT * FROM books WHERE id = :id");
    $checkStmt->bindParam(':id', $book_id);
    $checkStmt->execute();

    if ($checkStmt->rowCount() > 0) {
        // Prepare and execute the deletion query
        $deleteStmt = $pdo->prepare("DELETE FROM books WHERE id = :id");
        $deleteStmt->bindParam(':id', $book_id);

        if ($deleteStmt->execute()) {
            // Redirect to display books page after successful deletion
            header("Location: displaybooks.php?status=deleted");
            exit();
        } else {
            echo "Error deleting the book.";
        }
    } else {
        echo "No book found with the provided ID.";
    }
} else {
    echo "Invalid book ID.";
}
?>

