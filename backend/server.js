const express = require('express');
const multer = require('multer');
const cors = require('cors');
const { spawn } = require('child_process');
const fs = require('fs');

const app = express();

// Fix CORS
app.use(cors({
    origin: 'http://localhost:3000',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type']
}));

app.use(express.json());

const upload = multer({ dest: 'uploads/' });

if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

app.post('/predict', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No image uploaded' });
    }

    const imagePath = req.file.path;

    const python = spawn('/Users/harshasivaprasad/Downloads/anaconda3/envs/tf_env/bin/python', ['predict.py', imagePath]);

    let result = '';
    let error = '';

    python.stdout.on('data', (data) => {
        result += data.toString();
    });

    python.stderr.on('data', (data) => {
        error += data.toString();
    });

    python.on('close', (code) => {
        fs.unlinkSync(imagePath);

        if (code !== 0) {
            return res.status(500).json({ 
                error: 'Prediction failed', 
                details: error 
            });
        }

        try {
            const prediction = JSON.parse(result);
            res.json(prediction);
        } catch (e) {
            res.status(500).json({ 
                error: 'Invalid prediction output', 
                raw: result 
            });
        }
    });
});

// Test endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(8080, () => {
    console.log('Server running on port 8080');
});