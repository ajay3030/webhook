async function sendRequests() {
    const url = "http://127.0.0.1:8000/v1/webhooks/transactions";
    const numRequests = 10;

    console.log(`Sending ${numRequests} POST requests to ${url}...`);

    for (let i = 1; i <= numRequests; i++) {
        const payload = {
            transaction_id: `txn_perf_${i}`,
            source_account: "acc_user_1",
            destination_account: "acc_merchant_1",
            amount: 1000,
            currency: "INR"
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            // Log the status and response body for confirmation
            const responseText = await response.text();
            console.log(`Request ${i} (${payload.transaction_id}): Status ${response.status} | Response: ${responseText.substring(0, 50)}...`);

        } catch (error) {
            console.error(`Request ${i} failed:`, error.message);
        }
    }

    console.log("All requests sent.");
}

// Execute the function
sendRequests();