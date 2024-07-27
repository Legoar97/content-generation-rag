// src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import QueryForm from './components/QueryForm';

function App() {
    const [response, setResponse] = useState('');

    const handleQuerySubmit = async (query) => {
        const res = await axios.post('http://127.0.0.1:8000/generate_content/', { text: query });
        setResponse(res.data.response);
    };

    return (
        <div>
            <h1>Content Generation with Retrieval-Augmented Generation</h1>
            <QueryForm onSubmit={handleQuerySubmit} />
            {response && (
                <div>
                    <h2>Response:</h2>
                    <p>{response}</p>
                </div>
            )}
        </div>
    );
}

export default App;
