
import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardActionArea, CardMedia, CardContent, Typography, Box, Chip, Grid } from '@mui/material';
import './CaseStudies.css';

const CaseStudyTile = ({ study }) => {
    const { title, thumbnail, slug, tags } = study;

    // Flatten tags for display
    const allTags = [
        ...(tags.countries || []),
        ...(tags.industries || []),
        ...(tags.pillars || [])
    ];

    return (
        <Grid item xs={12} sm={6} md={4}>
            <Card className="case-study-tile">
                <CardActionArea component={Link} to={`/case-studies/${slug}`}>
                    <CardMedia
                        component="img"
                        height="140"
                        image={thumbnail || 'https://via.placeholder.com/300x140'} // Fallback image
                        alt={`Thumbnail for ${title}`}
                    />
                    <CardContent>
                        <Typography gutterBottom variant="h6" component="div" className="tile-title">
                            {title}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                            {allTags.map(tag => (
                                <Chip key={tag} label={tag} size="small" />
                            ))}
                        </Box>
                    </CardContent>
                </CardActionArea>
            </Card>
        </Grid>
    );
};

export default CaseStudyTile;
