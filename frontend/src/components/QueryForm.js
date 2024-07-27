// src/components/QueryForm.js
import React, { useState } from 'react';

function QueryForm({ onSubmit }) {
    const [query, setQuery] = useState('');

    const handleChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(query);
    };

    return (
        <form onSubmit={handleSubmit}>
            <label>Enter your query:</label>
            <input type="text" value={query} onChange={handleChange} />
            <button type="submit">Generate Content</button>
        </form>
    );
}

export default QueryForm;
