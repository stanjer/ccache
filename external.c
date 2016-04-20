
#include "ccache.h"

int init_external(const char *external)
{
	(void) external;
	return 0;
}

void
put_file_in_external(const char *external, const char *source,
                     const char *name, const char *suffix)
{
	char *external_path;
	struct stat st;

	external_path = get_path_in_cache(external, name, suffix);
	if (stat(source, &st) == 0) {
		cc_log("Storing %s%s in external", name, suffix);
		/* Skip already existing file */
		if (stat(external_path, &st) == 0) {
			free(external_path);
			return;
		}
		if (create_parent_dirs(external_path) != 0) {
			fatal("Failed to create parent directory for %s: %s",
			      external_path, strerror(errno));
		}
		if (copy_uncompressed_file(source, external_path, 0)) {
			cc_log("Failed to copy %s to %s: %s", source,
			       external_path, strerror(errno));
		}
	}
	free(external_path);
}

void
get_file_from_external(const char *external, const char *dest,
                       const char *name, const char *suffix)
{
	char *external_path;
	struct stat st;

	external_path = get_path_in_cache(external, name, suffix);
	if (stat(dest, &st) != 0) {
		cc_log("Getting %s%s from external", name, suffix);
		/* Skip external if missing */
		if (stat(external_path, &st) != 0 && errno == ENOENT) {
			free(external_path);
			return;
		}
		if (copy_uncompressed_file(external_path, dest, 0)) {
			cc_log("Failed to copy %s to %s: %s",
			       external_path, dest, strerror(errno));
		} else {
			stats_update_size(file_size(&st), 1);
		}
	}
	free(external_path);
}

int release_external(const char *external)
{
	(void) external;
	return 0;
}
