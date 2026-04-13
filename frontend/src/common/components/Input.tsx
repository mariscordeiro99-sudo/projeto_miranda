import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    classLabel?: string;
    classInput?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, classLabel, classInput, ...rest }) => {
    return (
        <div>
            {label && <label className={classLabel}>{label}</label>}
            <input className={classInput} {...rest} />
            {error && <span className="text-danger">{error}</span>}
        </div>
    );
};