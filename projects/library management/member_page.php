<?php
session_start();
require 'db.php';

$update_message = '';
$reservation_message = '';

// Handle book reservation
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['reserve'])) {
    if (!isset($_SESSION['user_id'])) {
        header("Location: projectlogin.php");
        exit();
    }
    
    try {
        $pdo->beginTransaction();
        
        $bookId = $_POST['reserve'];
        
        // Check availability
        $stmt = $pdo->prepare("SELECT number_of_books FROM Books WHERE id = ?");
        $stmt->execute([$bookId]);
        $book = $stmt->fetch();

        if (!$book || $book['number_of_books'] <= 0) {
            throw new Exception('Book is no longer available.');
        }

        // Check if user already has this book reserved
        $stmt = $pdo->prepare("SELECT id FROM Reserved_books WHERE book_id = ? AND user_id = ?");
        $stmt->execute([$bookId, $_SESSION['user_id']]);
        if ($stmt->rowCount() > 0) {
            throw new Exception('You have already reserved this book.');
        }

        // Reserve book
        $stmt = $pdo->prepare("INSERT INTO Reserved_books (book_id, user_id, final_return_date) 
                              VALUES (?, ?, DATE_ADD(NOW(), INTERVAL 14 DAY))");
        $stmt->execute([$bookId, $_SESSION['user_id']]);

        // Update book count
        $stmt = $pdo->prepare("UPDATE Books SET number_of_books = number_of_books - 1 WHERE id = ?");
        $stmt->execute([$bookId]);

        $pdo->commit();
        $reservation_message = "Book reserved successfully!";
    } catch (Exception $e) {
        $pdo->rollBack();
        $reservation_message = $e->getMessage();
    }
}

// Handle profile update
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_user'])) {
    if (!isset($_SESSION['user_id'])) {
        header("Location: projectlogin.php");
        exit();
    }
    
    $new_username = trim($_POST['new_username']);
    $new_password = $_POST['new_password'];
    
    try {
        if (!empty($new_username)) {
            $stmt = $pdo->prepare("SELECT id FROM Users WHERE username = ? AND id != ?");
            $stmt->execute([$new_username, $_SESSION['user_id']]);
            if ($stmt->rowCount() > 0) {
                throw new Exception("Username already exists!");
            }
            
            $stmt = $pdo->prepare("UPDATE Users SET username = ? WHERE id = ?");
            $stmt->execute([$new_username, $_SESSION['user_id']]);
            $_SESSION['username'] = $new_username;
        }
        
        if (!empty($new_password)) {
            $stmt = $pdo->prepare("UPDATE Users SET password = ? WHERE id = ?");
            $stmt->execute([md5($new_password), $_SESSION['user_id']]);
        }
        
        $update_message = "Profile updated successfully!";
    } catch (Exception $e) {
        $update_message = $e->getMessage();
    }
}

// Fetch books
$searchTerm = $_GET['search'] ?? '';
$searchType = $_GET['searchType'] ?? 'title';
$viewAll = isset($_GET['viewAll']) && $_GET['viewAll'] === 'true';

$query = "SELECT * FROM Books WHERE number_of_books > 0";
$params = [];

if (!$viewAll && !empty($searchTerm)) {
    switch ($searchType) {
        case 'title':
        case 'author':
        case 'genre':
            $query .= " AND $searchType LIKE ?";
            $params[] = "%$searchTerm%";
            break;
        case 'year':
            $query .= " AND YEAR(publication_date) = ?";
            $params[] = $searchTerm;
            break;
    }
}

$query .= " ORDER BY title ASC";
$stmt = $pdo->prepare($query);
$stmt->execute($params);
$books = $stmt->fetchAll();

// Fetch user's reserved books if viewing reservations
$reserved_books = [];
if (isset($_SESSION['user_id']) && isset($_GET['action']) && $_GET['action'] === 'reservations') {
    $stmt = $pdo->prepare("
        SELECT b.*, rb.final_return_date 
        FROM Books b 
        JOIN Reserved_books rb ON b.id = rb.book_id 
        WHERE rb.user_id = ?
        ORDER BY rb.final_return_date ASC
    ");
    $stmt->execute([$_SESSION['user_id']]);
    $reserved_books = $stmt->fetchAll();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Library Management System</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            min-height: 100vh;
            padding: 20px;
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
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .title {
            color: #EB5A3C;
            font-size: 32px;
            margin: 0;
        }
        .user-controls {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .button {
            padding: 10px 20px;
            background-color: #DF9755;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #357abd;
        }
        .search-section {
            margin-bottom: 30px;
        }
        .search-controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        .data {
            padding: 12px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .data:focus {
            border-color: #4a90e2;
            outline: none;
        }
        .books-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .books-table th,
        .books-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        .books-table th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .profile-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        .view-controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        .welcome-text {
            font-size: 18px;
            color: #666;
        }
        select.data {
            padding: 12px;
            min-width: 150px;
        }
        input[type="text"].data {
            flex: 1;
            min-width: 200px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Library Management System</h1>
            <div class="user-controls">
                <?php if (isset($_SESSION['user_id'])): ?>
                    <span class="welcome-text">Welcome, <?= htmlspecialchars($_SESSION['username']) ?></span>
                    <button onclick="toggleProfile()" class="button">Edit Profile</button>
                    <a href="?action=reservations" class="button">My Reservations</a>
                    <a href="logout.php" class="button">Logout</a>
                <?php else: ?>
                    <a href="projectlogin.php" class="button">Login</a>
                    <a href="signup.php" class="button">Sign Up</a>
                <?php endif; ?>
            </div>
        </div>

        <?php if (!empty($update_message)): ?>
            <div class="message success"><?= htmlspecialchars($update_message) ?></div>
        <?php endif; ?>

        <?php if (!empty($reservation_message)): ?>
            <div class="message <?= strpos($reservation_message, 'success') !== false ? 'success' : 'error' ?>">
                <?= htmlspecialchars($reservation_message) ?>
            </div>
        <?php endif; ?>

        <?php if (isset($_SESSION['user_id'])): ?>
            <div id="profileSection" class="profile-section">
                <h2>Update Profile</h2>
                <form method="POST" action="">
                    <input type="text" name="new_username" class="data" placeholder="New Username" style="width: 100%; margin-bottom: 15px;">
                    <input type="password" name="new_password" class="data" placeholder="New Password" style="width: 100%; margin-bottom: 15px;">
                    <button type="submit" name="update_user" class="button">Update Profile</button>
                </form>
            </div>
        <?php endif; ?>

        <?php if (isset($_SESSION['user_id']) && isset($_GET['action']) && $_GET['action'] === 'reservations'): ?>
            <h2>My Reserved Books</h2>
            <?php if (empty($reserved_books)): ?>
                <p>You have no reserved books.</p>
            <?php else: ?>
                <table class="books-table">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Author</th>
                            <th>Genre</th>
                            <th>Return Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($reserved_books as $book): ?>
                            <tr>
                                <td><?= htmlspecialchars($book['title']) ?></td>
                                <td><?= htmlspecialchars($book['author']) ?></td>
                                <td><?= htmlspecialchars($book['genre']) ?></td>
                                <td><?= htmlspecialchars($book['final_return_date']) ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
            <div class="view-controls">
                <a href="member_page.php" class="button">View Available Books</a>
            </div>
        <?php else: ?>
            <div class="view-controls">
                <a href="?viewAll=true" class="button">View All Books</a>
                <button onclick="toggleSearch()" class="button">Search Books</button>
            </div>

            <div id="searchSection" class="search-section" style="display: <?= $viewAll ? 'none' : 'block' ?>">
                <form method="GET" action="">
                    <div class="search-controls">
                        <select name="searchType" class="data">
                            <option value="title" <?= $searchType === 'title' ? 'selected' : '' ?>>Title</option>
                            <option value="author" <?= $searchType === 'author' ? 'selected' : '' ?>>Author</option>
                            <option value="genre" <?= $searchType === 'genre' ? 'selected' : '' ?>>Genre</option>
                            <option value="year" <?= $searchType === 'year' ? 'selected' : '' ?>>Publication Year</option>
                        </select>
                        <input type="text" name="search" class="data" placeholder="Enter search term..." 
                               value="<?= htmlspecialchars($searchTerm) ?>">
                        <button type="submit" class="button">Search</button>
                    </div>
                </form>
            </div>

            <?php if (empty($books)): ?>
                <p>No books found matching your criteria.</p>
            <?php else: ?>
                <table class="books-table">
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
                                <td><?= htmlspecialchars($book['title']) ?></td>
                                <td><?= htmlspecialchars($book['author']) ?></td>
                                <td><?= htmlspecialchars($book['genre']) ?></td>
                                <td><?= htmlspecialchars(date('Y-m-d', strtotime($book['publication_date']))) ?></td>
                                <td><?= htmlspecialchars($book['number_of_books']) ?></td>
                                <td>
                                    <form method="POST" style="margin: 0;">
                                        <input type="hidden" name="reserve" value="<?= $book['id'] ?>">
                                        <button type="submit" class="button">Reserve</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        <?php endif; ?>
    </div>

    <script>
        function toggleProfile() {
            const profileSection = document.getElementById('profileSection');
            profileSection.style.display = profileSection.style.display === 'none' ? 'block' : 'none';
        }

        function toggleSearch() {
            const searchSection = document.getElementById('searchSection');
            searchSection.style.display = searchSection.style.display ==='none' ? 'block' : 'none'; } </script>
</body> </html>
