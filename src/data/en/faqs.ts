/**
 * FAQs (English), grouped by page. Each group also outputs FAQPage schema.
 * Answers can contain simple inline HTML links.
 *
 * REVIEW: the payment, cancellation and ownership answers are sensible
 * defaults — make sure they match your actual contract terms.
 */
import { minimumTerms, monthlyPrices, setupFees, usd, websitePrices } from '../prices';
import { annualNote } from './pricing';

export interface FAQ {
  q: string;
  a: string;
}

export const faqs = {
  home: [
    {
      q: 'Do you only work with businesses near you?',
      a: 'No. We are based in Goose Creek, South Carolina, and work with small businesses anywhere in the United States. Calls, design reviews and reports all happen online, so location is never a problem.',
    },
    {
      q: 'Will I work with an account manager or the actual person doing the work?',
      a: 'You work directly with the founder. Same person on the free call, in the proposal and on the project. No call centers, no hand-offs.',
    },
    {
      q: 'Are your prices really published?',
      a: 'Yes. Every plan has a published starting price on our <a href="/pricing/">pricing page</a>. Your written proposal confirms the exact price before you pay anything.',
    },
    {
      q: 'Can you help me in Portuguese or Spanish?',
      a: 'Yes. We work in English, Portuguese and Spanish, and can create your website or social content in more than one language.',
    },
  ],

  webDesign: [
    {
      q: 'How much does a website cost?',
      a: `Our websites start at ${usd(websitePrices.landing)} for a one-page site, ${usd(websitePrices.essential)} for up to 5 pages and ${usd(websitePrices.professional)} for 6–10 pages. Your proposal gives you a fixed price before any work starts.`,
    },
    {
      q: 'How long does it take to build my website?',
      a: 'A landing page takes about a week. Most small-business sites take 2–6 weeks depending on size. The biggest factor is how quickly we receive your content and feedback.',
    },
    {
      q: 'Do I own my website?',
      a: 'Yes. Once the project is paid, the website, its content and your domain belong to you.',
    },
    {
      q: 'Do you write the text for my website?',
      a: 'Copywriting is included in the Premium Website. For other tiers we can write it for you as an add-on, or polish the text you provide.',
    },
    {
      q: 'What happens after the website launches?',
      a: `Essential and higher include 30 days of support after launch. After that, a Website Care plan (from ${usd(monthlyPrices.careBasic)}/mo) keeps your site updated, backed up and secure.`,
    },
    {
      q: 'Can I pay in installments?',
      a: annualNote.replace('12-month plans:', 'Yes, on 12-month plans:'),
    },
  ],

  localSeo: [
    {
      q: 'How long does local SEO take to work?',
      a: 'Most businesses see meaningful movement in 3–6 months. Some quick wins, like a fully optimized Google Business Profile, can help sooner. Anyone promising page one in two weeks is not being honest with you.',
    },
    {
      q: `Why is there a ${minimumTerms.localSeo}-month minimum?`,
      a: `SEO compounds over time. A ${minimumTerms.localSeo}-month minimum gives the work enough time to show real results, and lets us plan properly instead of chasing shortcuts.`,
    },
    {
      q: 'Do I need the one-time setup?',
      a: `Yes, for the Start and Growth plans. The ${usd(setupFees.localSeo)} setup fixes the foundation — your Google profile, on-page SEO, schema and directory listings. It is waived on 12-month plans.`,
    },
    {
      q: 'Can you guarantee a #1 ranking?',
      a: 'No one can honestly guarantee rankings — Google decides. What we guarantee is the work: clear deliverables every month and transparent reporting on your rankings, calls and website visits.',
    },
    {
      q: 'I serve several cities. Can you help me rank in all of them?',
      a: 'Yes. Local SEO Growth includes new city and service pages every month, and the Premium Website includes service-area pages built for exactly this.',
    },
    {
      q: 'What do I need to provide?',
      a: 'Access to your Google Business Profile and website, a list of your services and the areas you serve, and photos of your work if you have them. We handle the rest.',
    },
  ],

  socialMedia: [
    {
      q: 'Which platforms do you manage?',
      a: 'Instagram and Facebook on every plan. Social Plus and Social Pro can add LinkedIn or TikTok — up to 3 platforms in total.',
    },
    {
      q: 'Do I get to approve posts before they go live?',
      a: 'Yes. Every month you receive a content calendar to review. Nothing is published without your approval.',
    },
    {
      q: 'Where do the photos and videos come from?',
      a: 'We use your photos and videos, professional stock where it fits, and branded graphics we design. Social Pro includes one on-site content session per month.',
    },
    {
      q: `Is there a minimum contract?`,
      a: `Social media plans have a ${minimumTerms.social}-month minimum. After that, plans continue month to month.`,
    },
    {
      q: 'Is ad spend included in Social Pro?',
      a: 'Ads management is included. The ad spend itself is paid directly to Meta or TikTok and billed separately, so you always know exactly what goes to the ads.',
    },
  ],

  pricing: [
    {
      q: 'Why are your prices "starting at"?',
      a: 'Website prices depend on the number of pages and features. Monthly plans are fixed. Your written proposal always shows the exact price before you commit.',
    },
    {
      q: 'Are there setup fees?',
      a: `Local SEO has a ${usd(setupFees.localSeo)} one-time setup and social media has a ${usd(setupFees.social)} setup. ${annualNote}`,
    },
    {
      q: 'Is a website included in the bundles?',
      a: 'Bundles include Website Care (hosting, updates, backups and edits) for a website you already have or that we build. A new website is a separate one-time project, which can be paid in 6 interest-free installments on a 12-month plan.',
    },
    {
      q: 'Can I change or cancel my plan?',
      a: `You can upgrade at any time. Downgrades and cancellations take effect after the minimum term (${minimumTerms.localSeo} months for local SEO, ${minimumTerms.social} months for social media) with 30 days notice.`,
    },
    {
      q: 'How do I pay?',
      a: 'Monthly plans are billed automatically by card or bank transfer. Website projects are typically paid 50% to start and 50% at launch, unless you choose installments.',
    },
  ],
} satisfies Record<string, FAQ[]>;
