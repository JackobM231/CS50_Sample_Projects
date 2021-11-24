-- Keep a log of any SQL queries you execute as you solve the mystery.

-- 1)
SELECT description 
FROM crime_scene_reports
WHERE year = 2020 
AND month = 7 AND day = 28
AND street = "Chamberlin Street";
-- conclusions: 
    -- the hour of the theft 10:15
    -- there was 3 witnesses
    
    
-- 2)
-- listening to the trasscription of witnesses interviews
SELECT transcript 
FROM interviews
WHERE year = 2020 
AND month = 7 AND day = 28
AND transcript LIKE "%courthouse%";
-- conclusions: 
    -- the thief left the parking lot before 10:25
    -- the thief was withdrawing money at an ATM the same morning
    -- after leaving the court, talked to someone on the phone for less than a minute
    -- he planned to depart the next day on the first flight from Fiftyville


--3)
-- checking the first departure from Fiftyville
SELECT id, destination_airport_id, hour, minute
FROM flights
WHERE origin_airport_id =
    (SELECT id
    FROM airports
    WHERE city = "Fiftyville")
AND year = 2020 AND month = 7 AND day = 29
ORDER BY hour, minute ASC
LIMIT 1;

-- ESCAPED TO)
SELECT city
FROM airports
WHERE id = 4;
-- conclusions:
    -- the thief escaped to London

-- THIEF)
SELECT name, license_plate, phone_number, passport_number
FROM people
WHERE id IN
    (SELECT person_id
    FROM bank_accounts
    WHERE account_number IN
-- the thief was withdrawing money at an ATM the same morning
        (SELECT account_number
        FROM atm_transactions
        WHERE year = 2020 
        AND month = 7 AND day = 28
        AND transaction_type = "withdraw" 
        AND atm_location = "Fifer Street"))
-- the thief left the parking lot before 10:25
AND license_plate IN
    (SELECT license_plate
    FROM courthouse_security_logs
    WHERE year = 2020 
    AND month = 7 AND day = 28 
    AND hour = 10 AND minute > 15 AND minute < 25
    AND activity = "exit")
-- after leaving the court, talked to someone on the phone for less than a minute    
AND phone_number IN
    (SELECT caller
    FROM phone_calls
    WHERE year = 2020 
    AND month = 7 AND day = 28
    AND duration < 60)
-- he planned to depart the next day on the first flight from Fiftyville
AND passport_number IN
    (SELECT passport_number
    FROM passengers
    WHERE flight_id = 36);


-- ACCOMPLICE)
SELECT name, phone_number, passport_number
FROM people
WHERE phone_number IN
-- after leaving the court the thief, talked to someone on the phone for less than a minute
    (SELECT receiver
    FROM phone_calls
    WHERE year = 2020 
    AND month = 7 AND day = 28
    AND duration < 60 AND caller = "(367) 555-5533"); -- thief's phone number

