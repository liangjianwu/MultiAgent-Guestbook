const { Message } = require('../models/Message');

async function createMessage(req, res) {
    const { author, content } = req.body;
    
    if (!author || !content) {
        return res.status(400).json({ message: 'Author and content are required' });
    }
    
    if (Buffer.byteLength(author, 'utf8') > 255) {
        return res.status(400).json({ message: 'Author must be at most 255 bytes' });
    }
    
    try {
        const message = await Message.create({ author, content });
        res.status(201).json(message);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
}

async function listMessages(_req, res) {
    try {
        const messages = await Message.findAll({ order: [['created_at', 'DESC']] });
        res.status(200).json(messages);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
}

async function deleteMessage(req, res) {
    const id = parseInt(req.params.id);
    
    try {
        const count = await Message.destroy({ where: { id } });
        
        if (count === 0) {
            return res.status(404).json({ message: 'Message not found' });
        }
        
        res.status(204).send();
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
}

module.exports = { createMessage, listMessages, deleteMessage };
