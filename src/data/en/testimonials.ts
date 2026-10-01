/**
 * Testimonials (English).
 * ⚠️ PLACEHOLDERS — replace with real client quotes (with their permission).
 * Never publish invented testimonials. Set `placeholder: false` once real.
 * Testimonials with `placeholder: true` show a visible "Placeholder" label.
 */
export interface Testimonial {
  quote: string;
  name: string;
  role: string;
  service: string;
  placeholder: boolean;
}

export const testimonials: Testimonial[] = [
  {
    quote: '[TESTIMONIAL — replace with real client quote]',
    name: '[Client name]',
    role: '[Business type, City, State]',
    service: 'Website Design',
    placeholder: true,
  },
  {
    quote: '[TESTIMONIAL — replace with real client quote]',
    name: '[Client name]',
    role: '[Business type, City, State]',
    service: 'Local SEO',
    placeholder: true,
  },
  {
    quote: '[TESTIMONIAL — replace with real client quote]',
    name: '[Client name]',
    role: '[Business type, City, State]',
    service: 'Social Media',
    placeholder: true,
  },
];
