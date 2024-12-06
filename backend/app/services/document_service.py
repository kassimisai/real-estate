from typing import List, Optional
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere
from ..core.config import settings
from ..models.document import Document, DocumentStatus
import base64

class DocumentService:
    def __init__(self):
        self.api_client = ApiClient()
        self.api_client.host = settings.DOCUSIGN_HOST
        self.api_client.set_default_header("Authorization", f"Bearer {settings.DOCUSIGN_ACCESS_TOKEN}")
        self.envelopes_api = EnvelopesApi(self.api_client)
        self.account_id = settings.DOCUSIGN_ACCOUNT_ID

    async def create_envelope(self, document: Document, file_content: bytes, signers: List[dict]) -> str:
        """Create a DocuSign envelope for document signing"""
        
        # Create the document model
        doc = Document(
            document_base64=base64.b64encode(file_content).decode('utf-8'),
            name=document.title,
            file_extension='pdf',  # Assuming PDF format
            document_id='1'
        )

        # Create signers
        envelope_signers = []
        sign_here_tabs = []
        
        for i, signer in enumerate(signers, 1):
            sign_here = SignHere(
                anchor_string="/sig/",  # Assuming we use this anchor in documents
                anchor_units="pixels",
                anchor_y_offset="10",
                anchor_x_offset="20"
            )
            
            signer_obj = Signer(
                email=signer['email'],
                name=signer['name'],
                recipient_id=str(i),
                routing_order=str(i),
                sign_here_tabs=[sign_here]
            )
            
            envelope_signers.append(signer_obj)

        # Create envelope definition
        envelope_definition = EnvelopeDefinition(
            email_subject=f"Please sign {document.title}",
            documents=[doc],
            recipients={'signers': envelope_signers},
            status="sent"
        )

        try:
            # Create and send envelope
            result = self.envelopes_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition
            )
            return result.envelope_id
        except Exception as e:
            raise Exception(f"Failed to create envelope: {str(e)}")

    async def get_envelope_status(self, envelope_id: str) -> DocumentStatus:
        """Get the status of a DocuSign envelope"""
        try:
            result = self.envelopes_api.get_envelope(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            # Map DocuSign status to our DocumentStatus
            status_mapping = {
                "sent": DocumentStatus.PENDING_SIGNATURE,
                "completed": DocumentStatus.SIGNED,
                "voided": DocumentStatus.CANCELLED
            }
            
            return status_mapping.get(result.status, DocumentStatus.DRAFT)
        except Exception as e:
            raise Exception(f"Failed to get envelope status: {str(e)}")

    async def void_envelope(self, envelope_id: str, void_reason: str) -> bool:
        """Void a DocuSign envelope"""
        try:
            self.envelopes_api.void_envelope(
                account_id=self.account_id,
                envelope_id=envelope_id,
                void_envelope_reason=void_reason
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to void envelope: {str(e)}")

    async def create_embedded_signing_url(self, envelope_id: str, signer_email: str, signer_name: str) -> str:
        """Create an embedded signing URL for a recipient"""
        try:
            recipient_view_request = {
                'authentication_method': 'email',
                'client_user_id': signer_email,
                'recipient_id': '1',
                'return_url': f"{settings.APP_URL}/documents/signing-complete",
                'user_name': signer_name,
                'email': signer_email
            }

            result = self.envelopes_api.create_recipient_view(
                account_id=self.account_id,
                envelope_id=envelope_id,
                recipient_view_request=recipient_view_request
            )

            return result.url
        except Exception as e:
            raise Exception(f"Failed to create embedded signing URL: {str(e)}")
