<?php
$host = 'localhost'; // Database host
$dbname = 'LibraryManagement'; // Database name
$username = 'root'; // Database username
$password = ''; // Database password

try {
    // Create a PDO instance
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    // Set the PDO error mode to exception
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Fetch the number of users
    $userQuery = "SELECT COUNT(*) as user_count FROM Users";
    $bookQuery = "SELECT SUM(number_of_books) as total_books FROM Books";

    $userStmt = $pdo->prepare($userQuery);
    $bookStmt = $pdo->prepare($bookQuery);

    $userStmt->execute();
    $bookStmt->execute();

    $userCount = $userStmt->fetch(PDO::FETCH_ASSOC)['user_count'];
    $totalBooks = $bookStmt->fetch(PDO::FETCH_ASSOC)['total_books'];
} catch (PDOException $e) {
    // Handle the exception if the connection fails
    die("Connection failed: " . $e->getMessage());
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Users and Books Bar Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 150px;
            background-image: url("lib.jpg");
            background-repeat: no-repeat;
            background-size: cover;
        }
        .container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #DF9755;
        }
        canvas {
            display: block;
            margin: auto;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Number of Users and Books</h1>
    <canvas id="myChart" width="400" height="200"></canvas>
</div>

<script>
    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',  // Bar chart type
        data: {
            labels: ['Users', 'Books'], // Labels for the bar chart
            datasets: [{
                label: 'Count',
                data: [<?php echo $userCount; ?>, <?php echo $totalBooks; ?>], // PHP variables passed to JS
                backgroundColor: ['#3498db', '#2ecc71'], // Colors for the bars
                borderColor: ['#2980b9', '#27ae60'], // Border colors
                borderWidth: 1
            }]
        },
        options: {
            responsive: true, // Makes the chart responsive
            scales: {
                y: {
                    beginAtZero: true, // Start y-axis at zero
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            }
        }
    });
</script>

</body>
</html>


