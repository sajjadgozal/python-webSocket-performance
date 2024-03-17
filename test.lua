wrk.method = "POST"
wrk.headers["Content-Type"] = "text/plain"
wrk.body = "Hello, WebSocket!"
wrk.websocket_init = function(ws)
    ws:send("Hello, WebSocket!")
    local response = ws:receive()
    if response == "Received: Hello, WebSocket!" then
        print("Connection established successfully")
    else
        print("Failed to establish connection")
    end
end