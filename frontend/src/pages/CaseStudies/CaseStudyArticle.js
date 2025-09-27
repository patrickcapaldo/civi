
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Container, Typography, Box, CircularProgress, Paper, Chip } from '@mui/material';
import './CaseStudies.css'; // Reusing the same CSS file for consistency

const CaseStudyArticle = ({ headerHeight }) => {
    const { slug } = useParams();
    const [article, setArticle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchArticle = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/case_studies/articles/${slug}.json`);
                if (!response.ok) {
                    throw new Error(`Article not found: ${response.statusText}`);
                }
                const data = await response.json();
                setArticle(data);
            } catch (e) {
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };

        fetchArticle();
    }, [slug]);

    if (loading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Typography color="error" sx={{ mt: 4, textAlign: 'center' }}>Error: {error}</Typography>;
    }

    if (!article) {
        return null; // Or a more specific 'not found' component
    }

    const allTags = [
        ...(article.tags.countries || []),
        ...(article.tags.industries || []),
        ...(article.tags.pillars || [])
    ];

    return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
            <Paper elevation={3} sx={{ p: { xs: 2, md: 4 } }}>
                <Typography variant="h3" component="h1" gutterBottom>
                    {article.title}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                    By {article.author} on {new Date(article.date).toLocaleDateString()}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                    {allTags.map(tag => (
                        <Chip key={tag} label={tag} size="small" />
                    ))}
                </Box>
                <Box
                    component="img"
                    src={article.thumbnail}
                    alt={`Thumbnail for ${article.title}`}
                    sx={{ width: '100%', maxHeight: '400px', objectFit: 'cover', mb: 2, borderRadius: 1 }}
                />
                <Typography component="div" className="markdown-content">
                    <ReactMarkdown>{article.content}</ReactMarkdown>
                </Typography>
            </Paper>
        </Container>
    );
};

export default CaseStudyArticle;
