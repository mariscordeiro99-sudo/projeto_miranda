import { useState, useCallback } from 'react';

export const useProfileImage = () => {
    const [profileImage, setProfileImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];

        if (file) {
            setProfileImage(file);
            const previewUrl = URL.createObjectURL(file);
            setImagePreview(previewUrl);
        }
    };

    const clearImage = useCallback(() => {
        setProfileImage(null);
        setImagePreview(null);
    }, []);

    return {
        profileImage,
        imagePreview,
        handleImageChange,
        clearImage
    };
};