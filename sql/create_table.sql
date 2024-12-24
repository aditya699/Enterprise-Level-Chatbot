
-- Create tables (in correct order)
CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    picture_url VARCHAR(1024),
    google_id VARCHAR(255) UNIQUE,
    created_at DATETIME DEFAULT GETDATE(),
    last_login DATETIME
);

CREATE TABLE Sessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES Users(id),
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE Messages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES Users(id),
    content TEXT NOT NULL,
    is_user_message BIT NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);