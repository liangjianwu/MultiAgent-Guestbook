const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
  process.env.DB_DATABASE || 'guestbook_demo',
  process.env.DB_USER || 'leo',
  process.env.DB_PASSWORD || 'hvcsL3HB0M77cgHjAsJ0',
  {
    host: process.env.DB_HOST || '172.17.0.1',
    port: process.env.DB_PORT || 3306,
    dialect: 'mysql',
    logging: false,
  }
);

module.exports = sequelize;
