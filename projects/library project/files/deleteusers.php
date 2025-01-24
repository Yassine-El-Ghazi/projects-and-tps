<?php

require 'db.php';

if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['id'])) {
    $id = intval($_GET['id']); // Convertir en entier pour plus de sécurité

    if ($id > 0) { // Vérifier si l'ID est valide
        try {
            $query = "DELETE FROM Users WHERE id = :id";
            $stmt = $pdo->prepare($query);
            $stmt->bindParam(':id', $id, PDO::PARAM_INT); // Lier avec un type explicite

            if ($stmt->execute()) {
                // Rediriger avec un message de succès
                header("Location: user_dis.php?success=deleted");
                exit();
            } else {
                echo "Error: Failed to delete the user.";
            }
        } catch (PDOException $e) {
            echo "Error: " . htmlspecialchars($e->getMessage());
        }
    } else {
        // Rediriger en cas d'ID non valide
        header("Location: user_dis.php?error=invalid_id");
        exit();
    }
} else {
    // Rediriger si la requête ou l'ID n'est pas valide
    header("Location: user_dis.php?error=missing_id");
    exit();
}


