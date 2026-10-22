from django.db import migrations


LEGACY_POST_SLUG = 'watch-this-the-story-of-my-comeback'


def populate_legacy_reel_metadata(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    post = Post.objects.using(schema_editor.connection.alias).filter(
        slug=LEGACY_POST_SLUG
    ).first()
    if post is None:
        return

    update_fields = []
    if not post.reel_title:
        post.reel_title = 'Recovery Reel'
        update_fields.append('reel_title')
    if not post.reel_description:
        post.reel_description = 'Moments from the comeback — rehab, sweat, belief.'
        update_fields.append('reel_description')
    if update_fields:
        post.save(
            using=schema_editor.connection.alias,
            update_fields=update_fields,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_post_reel_metadata'),
    ]

    operations = [
        migrations.RunPython(
            populate_legacy_reel_metadata,
            migrations.RunPython.noop,
        ),
    ]
