import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    classLabel?: string;
    classInput?: string;
    classError?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, classLabel, classInput, classError, ...rest }) => {
    return (
        <div>
            {label && <label className={classLabel}>{label}</label>}
            <input 
                className={`${classInput} ${error ? "is-invalid" : ""}`} 
                {...rest} 
            />
            {error && <span className={classError || "text-danger"}>{error}</span>}
        </div>
    );
};