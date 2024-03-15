import { Button, TextareaAutosize, styled } from '@mui/material';

export const StyledForm = styled('form')({
    display: 'flex',
    justifyContent: 'center',
    marginTop: '20px',

    flexDirection: 'column',
    gap: '8px',
    width: '50%',
    margin: 'auto',
});

export const StyledInput = styled('input')({
    padding: '10px',
    fontSize: '16px',
    border: '2px solid #FF914D',
    borderRadius: '5px',
    width: '300px',
});

export const StyledTextareaAutosize = styled(TextareaAutosize)({
    width: '100%', // Make sure the textarea fills the form width
    padding: '8px',
    borderColor: '#FF914D', // Example border color, adjust as needed
    borderRadius: '4px',
    resize: 'none', // Disable manual resize
    fontSize: '16px',
    fontFamily: 'inherit', // To keep the font consistent with the rest of your UI
    '&:focus': {
        outline: '2px solid #FF914D', // Focus state
    },
});

export const StyledButton = styled(Button)({
    marginTop: '8px', // Adjust spacing as needed
    background: '#FF914D', // Example color, adjust according to your design
    color: '#FFFFFF',
    '&:hover': {
        background: '#E57F35', // Darker shade for hover state
    },
});
