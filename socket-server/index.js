const { Server } = require("socket.io");

const io = new Server({
  cors: {
    origin: [
      "http://localhost:8000",
      "http://0.0.0.0:8000",
      "http://localhost:5173"
    ],
    methods: ["GET", "POST"]
  }
});

let onlineUsers = [];

io.on("connection", (socket) => {
  socket.on("addNewUser", (userId) => {
    if (!onlineUsers.some((user) => user.userId === userId)) {
      onlineUsers.push({ userId, socketId: socket.id });
    }
    io.emit("getOnlineUsers", onlineUsers);
  });

  socket.on("sendMessage", (message) => {
    const user = onlineUsers.find((u) => u.userId === message.recipientId);
    if (user) {
      io.to(user.socketId).emit("getMessage", message);
      io.to(user.socketId).emit("getNotification", {
        senderId: message.senderId,
        message: message.text,
        isRead: false,
        date: new Date()
      });
    }
  });

  socket.on("sendOrder", (order) => {
    const receiver = onlineUsers.find((u) => u.userId === order.receiverId);
    if (receiver) {
      io.to(receiver.socketId).emit("getOrder", order);
    }
  });

  socket.on("disconnect", () => {
    onlineUsers = onlineUsers.filter((u) => u.socketId !== socket.id);
    io.emit("getOnlineUsers", onlineUsers);
  });
});

io.listen(3000);
