import { styled } from '@mui/material';

export const TitleComponentContainer = styled('div')({
    textAlign: 'center',
    color: '#F9D342', // Bright Yellow for a Sunny Vibe
    position: 'relative',
    marginBottom: '20px',
});

export const TitleComponentHeading = styled('h1')({
    fontSize: '48px',
    background: 'linear-gradient(#FFD55A, #FF914D)',
    '-webkit-background-clip': 'text',
    '-webkit-text-fill-color': 'transparent',
    backgroundClip: 'text',
    color: 'transparent',
});

export const SunAnimation = styled('div')({
    width: '100px',
    height: '100px',
    backgroundColor: '#F9D342',
    borderRadius: '50%',
    position: 'absolute',
    top: '-50px',
    right: '50%',
    transform: 'translateX(-50%)', // Center the sun
    animation: '$rotate 10s infinite linear',
    '@keyframes rotate': {
        from: {
            transform: 'rotate(0deg) translateX(50px) rotate(0deg)',
        },
        to: {
            transform: 'rotate(360deg) translateX(50px) rotate(-360deg)',
        },
    },
});
