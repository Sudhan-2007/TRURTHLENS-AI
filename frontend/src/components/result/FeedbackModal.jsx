import React, { useState } from 'react';
import { feedbackApi } from '../../api/feedback';

export default function FeedbackModal({ isOpen, onClose, submissionId }) {
  const [rating, setRating] = useState(0);
  const [comments, setComments] = useState('');
  const [altSource, setAltSource] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const payload = {
        submission_id: submissionId,
        rating,
        comments: comments || null,
        alternative_sources: altSource ? [altSource] : null
      };
      await feedbackApi.submitFeedback(payload);
      setSuccess(true);
      setTimeout(() => {
        onClose();
        setSuccess(false);
        setRating(0);
        setComments('');
        setAltSource('');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-800">
        <h2 className="mb-4 text-xl font-bold text-slate-900 dark:text-white">Provide Feedback</h2>
        
        {success ? (
          <div className="rounded-lg bg-green-50 p-4 text-center text-green-700 dark:bg-green-900/30 dark:text-green-400">
            Thank you for your feedback! It helps improve TruthLens AI.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
                How accurate was this assessment?
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className={`text-2xl transition-colors ${rating >= star ? 'text-yellow-400' : 'text-slate-300 dark:text-slate-600'} hover:text-yellow-300`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
                Comments (Optional)
              </label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white p-2 text-slate-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-600 dark:bg-slate-700 dark:text-white"
                rows="3"
                placeholder="Why did you give this rating?"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
                Alternative Source URL (Optional)
              </label>
              <input
                type="url"
                value={altSource}
                onChange={(e) => setAltSource(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white p-2 text-slate-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-600 dark:bg-slate-700 dark:text-white"
                placeholder="https://..."
              />
            </div>

            {error && <div className="text-sm text-red-500">{error}</div>}

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
