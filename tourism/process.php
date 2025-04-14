<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

try {
    // Database connection
    $db = new mysqli('localhost', 'root', '', 'iitb_scheme');

    if ($db->connect_error) {
        throw new Exception("Connection failed: " . $db->connect_error);
    }

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Convert preferred states array to string
        $preferredStates = isset($_POST['preferredStates']) ? implode(', ', $_POST['preferredStates']) : '';
        
        // Convert categories array to string
        $categories = isset($_POST['categories']) ? implode(', ', $_POST['categories']) : '';

        // Prepare the SQL statement
        $sql = "INSERT INTO users (
            full_name, dob, gender, aadhaar, mobile, email, 
            state, city, pincode, previous_travel, 
            preferred_states, travel_purpose, special_categories, 
            transport_mode, upi_id, gov_benefits
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

        $stmt = $db->prepare($sql);
        
        if ($stmt === false) {
            throw new Exception("Prepare failed: " . $db->error);
        }

        $previousTravel = isset($_POST['previousTravel']) && $_POST['previousTravel'] === 'yes' ? 1 : 0;
        $govBenefits = isset($_POST['govBenefits']) && $_POST['govBenefits'] === 'yes' ? 1 : 0;

        $stmt->bind_param("sssssssssisssssi",
            $_POST['fullName'],
            $_POST['dob'],
            $_POST['gender'],
            $_POST['aadhaar'],
            $_POST['mobile'],
            $_POST['email'],
            $_POST['state'],
            $_POST['city'],
            $_POST['pincode'],
            $previousTravel,
            $preferredStates,
            $_POST['travelPurpose'],
            $categories,
            $_POST['transport'],
            $_POST['upiId'],
            $govBenefits
        );

        if ($stmt->execute()) {
            $userId = $db->insert_id;

            // Handle file upload
            if (isset($_FILES['aadhaarDoc']) && $_FILES['aadhaarDoc']['error'] === 0) {
                $uploadDir = 'uploads/';
                if (!file_exists($uploadDir)) {
                    mkdir($uploadDir, 0777, true);
                }

                $fileName = $userId . '_aadhaar.' . pathinfo($_FILES['aadhaarDoc']['name'], PATHINFO_EXTENSION);
                $filePath = $uploadDir . $fileName;

                if (move_uploaded_file($_FILES['aadhaarDoc']['tmp_name'], $filePath)) {
                    // Update user record with document path
                    $db->query("UPDATE users SET aadhaar_doc = '$fileName' WHERE id = $userId");
                }
            }

            echo json_encode(['success' => true]);
        } else {
            throw new Exception("Execute failed: " . $stmt->error);
        }

        $stmt->close();
    }
} catch (Exception $e) {
    error_log($e->getMessage());
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}

$db->close();
?>