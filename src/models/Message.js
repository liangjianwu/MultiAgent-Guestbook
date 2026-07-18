const { DataTypes, Model } = require('sequelize');
const sequelize = require('../config/database');

class Message extends Model {}

Message.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true,
    },
    author: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
    content: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
  },
  {
    sequelize,
    modelName: 'Message',
    tableName: 'messages',
    timestamps: true,
    // created_at 和 updated_at 由 Sequelize timestamps=true 自动生成
    updatedAt: 'updated_at',
    createdAt: 'created_at',
  }
);

async function syncDatabase() {
  await sequelize.sync({ alter: true });
}

module.exports = { Message, syncDatabase, DataTypes, Model };
