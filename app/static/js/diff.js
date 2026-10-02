// Diff helper for integration if needed, beyond Alpine component.
// The Diff object is exposed globally by the CDN import.
window.humanizerDiffHelper = {
    // Optionally export custom diff utility functions
    diffSentences: function(oldStr, newStr) {
        if (window.Diff) {
            return Diff.diffSentences(oldStr, newStr);
        }
        return null;
    }
};
