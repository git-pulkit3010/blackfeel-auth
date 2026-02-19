export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Terms of Service</h1>
        <p className="text-sm text-gray-500 mb-8">Last updated: February 19, 2026</p>

        <div className="prose prose-blue max-w-none">
          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">1. Acceptance of Terms</h2>
            <p className="text-gray-700 leading-relaxed">
              By accessing and using this service, you accept and agree to be bound by the terms and provision of this agreement. 
              If you do not agree to abide by these terms, please do not use this service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">2. Use License</h2>
            <p className="text-gray-700 leading-relaxed">
              Permission is granted to temporarily access the materials (information or software) on the service for personal, 
              non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this 
              license you may not:
            </p>
            <ul className="list-disc list-inside text-gray-700 mt-3 space-y-1">
              <li>Modify or copy the materials</li>
              <li>Use the materials for any commercial purpose or for any public display</li>
              <li>Attempt to decompile or reverse engineer any software contained on the service</li>
              <li>Remove any copyright or other proprietary notations from the materials</li>
              <li>Transfer the materials to another person or mirror the materials on any other server</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">3. User Accounts</h2>
            <p className="text-gray-700 leading-relaxed">
              To access certain features of the service, you may be required to create an account. You are responsible for:
            </p>
            <ul className="list-disc list-inside text-gray-700 mt-3 space-y-1">
              <li>Maintaining the security of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us immediately of any unauthorized access</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">4. Privacy</h2>
            <p className="text-gray-700 leading-relaxed">
              Your use of the service is also governed by our Privacy Policy. Please review our Privacy Policy to understand 
              our practices regarding the collection and use of your personal information.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">5. Disclaimer</h2>
            <p className="text-gray-700 leading-relaxed">
              The materials on the service are provided on an &apos;as is&apos; basis. We make no warranties, expressed or implied, 
              and hereby disclaim and negate all other warranties including, without limitation, implied warranties or conditions 
              of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">6. Limitations</h2>
            <p className="text-gray-700 leading-relaxed">
              In no event shall we or our suppliers be liable for any damages (including, without limitation, damages for loss 
              of data or profit, or due to business interruption) arising out of the use or inability to use the materials on 
              the service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">7. Modifications</h2>
            <p className="text-gray-700 leading-relaxed">
              We may revise these terms of service at any time without notice. By using this service you are agreeing to be 
              bound by the then current version of these terms of service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">8. Governing Law</h2>
            <p className="text-gray-700 leading-relaxed">
              These terms and conditions are governed by and construed in accordance with applicable laws and you irrevocably 
              submit to the exclusive jurisdiction of the courts in that location.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">9. Contact Information</h2>
            <p className="text-gray-700 leading-relaxed">
              If you have any questions about these Terms of Service, please contact us at support@example.com.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
