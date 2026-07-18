const app = require('./app');
const sequelize = require('./config/database');

(async () => {
  await sequelize.sync({ alter: true });
  const server = app.listen(6008, (err) => {
    if (err) throw err;
    console.log('Server is running on port 6008');
  });
  module.exports = server;
})();
