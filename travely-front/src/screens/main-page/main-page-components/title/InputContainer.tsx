import React, { useState } from 'react';
import { StyledForm, StyledButton, StyledTextareaAutosize } from './InputContainer.s';
import { sendTripInformation } from '../../../../DAL/server-requests/TripDAL';

export const InputComponent = () => {
    const [inputValue, setInputValue] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        console.log("User's travel desire:", inputValue);
        const res = await sendTripInformation(inputValue);
        if (res) {
            console.log('Trip information sent successfully');
        } else {
            console.log('Failed to send trip information');
        }
    };

    return (
        <StyledForm onSubmit={handleSubmit}>
            <StyledTextareaAutosize
                minRows={3}
                maxRows={6}
                placeholder="What's your dream destination?"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
            />
            <StyledButton type="submit" variant="contained">
                Submit
            </StyledButton>
        </StyledForm>
    );
};
