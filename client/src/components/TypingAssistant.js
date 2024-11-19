import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import './TypingAssistant.css';

const socket = io('http://localhost:5000');

const TypingAssistant = () => {
    const [text, setText] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [domain, setDomain] = useState('general');
    const [isLoading, setIsLoading] = useState(false);
    const [stats, setStats] = useState({
        words: 0,
        chars: 0,
        wpm: 0,
        accuracy: 100,
        level: 1,
        xp: 0,
        streak: 0
    });
    const [achievements, setAchievements] = useState([]);
    const [showStats, setShowStats] = useState(false);
    const timeoutRef = useRef(null);
    const sessionStartRef = useRef(Date.now());

    useEffect(() => {
        socket.on('correction-result', (corrections) => {
            setSuggestions(corrections);
            setIsLoading(false);
        });

        socket.on('stats-update', (newStats) => {
            setStats(newStats);
        });

        socket.on('achievement-earned', (achievement) => {
            setAchievements(prev => [...prev, achievement]);
            // Show achievement notification
            showAchievementNotification(achievement);
        });

        return () => {
            socket.off('correction-result');
            socket.off('stats-update');
            socket.off('achievement-earned');
        };
    }, []);

    const handleTextChange = (e) => {
        const newText = e.target.value;
        setText(newText);

        // Update word count
        const words = newText.trim().split(/\s+/).filter(word => word.length > 0);
        const chars = newText.length;

        // Calculate WPM
        const minutesElapsed = (Date.now() - sessionStartRef.current) / 60000;
        const wpm = Math.round(words.length / minutesElapsed);

        // Update local stats
        setStats(prev => ({
            ...prev,
            words: words.length,
            chars,
            wpm: wpm || 0
        }));

        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        if (newText.trim()) {
            setIsLoading(true);
            timeoutRef.current = setTimeout(() => {
                socket.emit('text-correction', { 
                    text: newText, 
                    domain,
                    stats: {
                        words: words.length,
                        chars,
                        wpm
                    }
                });
            }, 200);  
        } else {
            setSuggestions([]);
        }
    };

    const handleDomainChange = (e) => {
        setDomain(e.target.value);
        if (text.trim()) {
            setIsLoading(true);
            socket.emit('text-correction', { text, domain: e.target.value });
        }
    };

    const applySuggestion = (correction) => {
        setText(correction);
        setSuggestions([]);
        
        // Track correction for stats
        socket.emit('correction-applied', {
            original: text,
            corrected: correction
        });
    };

    const showAchievementNotification = (achievement) => {
        // Create and show a toast notification
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-icon">🏆</div>
            <div class="achievement-text">
                <h4>Achievement Unlocked!</h4>
                <p>${achievement}</p>
            </div>
        `;
        document.body.appendChild(notification);

        // Remove notification after animation
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    };

    return (
        <div className="typing-assistant">
            <h1>AI Typing Assistant</h1>
            
            <div className="stats-bar">
                <div className="stat">
                    <span className="stat-label">Level</span>
                    <span className="stat-value">{stats.level}</span>
                </div>
                <div className="stat">
                    <span className="stat-label">XP</span>
                    <span className="stat-value">{stats.xp}/1000</span>
                    <div className="xp-bar">
                        <div 
                            className="xp-progress" 
                            style={{width: `${(stats.xp % 1000) / 10}%`}}
                        />
                    </div>
                </div>
                <div className="stat">
                    <span className="stat-label">Streak</span>
                    <span className="stat-value">🔥 {stats.streak} days</span>
                </div>
                <div className="stat">
                    <span className="stat-label">WPM</span>
                    <span className="stat-value">{stats.wpm}</span>
                </div>
                <div className="stat">
                    <span className="stat-label">Accuracy</span>
                    <span className="stat-value">{stats.accuracy}%</span>
                </div>
            </div>

            <div className="domain-selector">
                <label htmlFor="domain">Domain:</label>
                <select id="domain" value={domain} onChange={handleDomainChange}>
                    <option value="general">General</option>
                    <option value="technical">Technical</option>
                    <option value="medical">Medical</option>
                    <option value="academic">Academic</option>
                </select>
            </div>

            <div className="input-container">
                <textarea
                    value={text}
                    onChange={handleTextChange}
                    placeholder="Start typing here..."
                    className="text-input"
                />
                {isLoading && <div className="loading-spinner" />}
            </div>

            {suggestions.length > 0 && (
                <div className="suggestions">
                    <h3>Suggestions:</h3>
                    <ul>
                        {suggestions.map((suggestion, index) => (
                            <li
                                key={index}
                                onClick={() => applySuggestion(suggestion.correction)}
                                className="suggestion-item"
                            >
                                <span className="correction">{suggestion.correction}</span>
                                <span className="confidence">
                                    {Math.round(suggestion.confidence * 100)}% confident
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            <button 
                className="stats-toggle"
                onClick={() => setShowStats(!showStats)}
            >
                {showStats ? 'Hide Stats' : 'Show Stats'}
            </button>

            {showStats && (
                <div className="detailed-stats">
                    <h3>Your Achievements</h3>
                    <div className="achievements-list">
                        {achievements.map((achievement, index) => (
                            <div key={index} className="achievement-item">
                                🏆 {achievement}
                            </div>
                        ))}
                    </div>
                    
                    <h3>Session Statistics</h3>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h4>Total Words</h4>
                            <p>{stats.words}</p>
                        </div>
                        <div className="stat-card">
                            <h4>Characters</h4>
                            <p>{stats.chars}</p>
                        </div>
                        <div className="stat-card">
                            <h4>WPM</h4>
                            <p>{stats.wpm}</p>
                        </div>
                        <div className="stat-card">
                            <h4>Accuracy</h4>
                            <p>{stats.accuracy}%</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TypingAssistant;
