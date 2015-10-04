#ifndef MDFOUR_H
#define MDFOUR_H

#include <stddef.h>
#include <inttypes.h>

#ifdef HAVE_OPENSSL_MD4_H
#include <openssl/md4.h>
#endif

#ifndef USE_CRYPTO
struct mdfour {
	uint32_t A, B, C, D;
	size_t totalN;
	unsigned char tail[64];
	size_t tail_len;
	int finalized;
};
#else /* USE_CRYPTO */
struct mdfour {
	MD4_CTX ctx;
	size_t totalN;
};
#endif

void mdfour_begin(struct mdfour *md);
void mdfour_update(struct mdfour *md, const unsigned char *in, size_t n);
void mdfour_result(struct mdfour *md, unsigned char *out);

#endif
