# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str  # smart_unicode, force_unicode,

from taggit.managers import TaggableManager
from filebrowser.fields import FileBrowseField

from utils.managers import PublishedManager
from utils import minitags as tags  # import dropdown  #, ul, li
from utils.minitags2 import TagStream
from utils.tagstream22 import TagStream as TagStream22
#from utils.tagstream24_5 import TagStream as TagStream24_5
from utils import spreadto5


#### Misc abstract base classes - Publishable mixin (move to utils or more generic place), ImageBase ABC, Imageable

class Publishable (models.Model):  # ABC
    published   = models.BooleanField (default=True)
    created     = models.DateTimeField (auto_now_add=True)
    updated     = models.DateTimeField (auto_now=True)

    objects     = PublishedManager()

    class Meta:
        abstract = True


class ImageBase (models.Model):  # ABC
    #images_dir  = "set/me/in/descendant/class"
    #
    #def get_images_dir (self):
    #  return self.images_dir
    #
    # Nope, the callable is only in the Mezzanine fork.  :-(
    #
    #image       = FileBrowseField(max_length=200, directory=get_images_dir)

    title       = models.CharField (max_length=70, blank=True, help_text='If present, used for mouseover title / alt.')
    caption     = models.CharField (max_length=200, blank=True, help_text='If present, used for image caption.')
    sortorder   = models.IntegerField (default=100, help_text='Top one is the default image')

    def tag (self):
        i = self.image
        obj = getattr (self, self.fk_name)
        #title = self.title or ('eRacks %s %s' % (obj.sku, i.filename))
        title = self.title or ('%s %s' % (obj.name, i.filename))
        return tags.img (src=i.url, title=title, alt=title, width=i.width, height=i.height)

    def __unicode__ (self):
        return self.tag()

    class Meta:
        ordering = ['sortorder',]
        abstract = True


class Imageable (models.Model):  # ABC
    def image (self):  # primary_image - first one in list!
        img = self.images.published()[:1]
        if img:
            return img [0]

    class Meta:
        abstract = True


#### eRacks product tables - Categories (should rename Category)
# both P-O-C-PO-POC, and P-O-C-PO-OL

class CategoryImage (Publishable, ImageBase):
    fk_name     = 'category'
    images_dir  = "images/categories/"
    image       = FileBrowseField(max_length=200, directory = images_dir)
    category    = models.ForeignKey ('Categories', related_name = 'images')

class Categories (Imageable):
    name        = models.CharField (max_length=50,  help_text='Category Name - Capitals, spaces OK. slugified for urls.')
    slug        = models.SlugField (                help_text='Category url name - slugified from name field.')
    title       = models.CharField (max_length=100, blank=True, help_text='If present, used for page title (useful for SEO).')
    blurb       = models.TextField (blank=True,     help_text='Short description, typically a few lines, HTML OK.')
    description = models.TextField (blank=True,     help_text='Detailed description, HTML OK. Used for cetegory page.')
    comments    = models.TextField (blank=True,     help_text='Internal notes and comments.  Please add dates & your initials')
    sortorder   = models.IntegerField (default=100)

    meta_title       = models.CharField (max_length=512, blank=True, help_text="Meta title")
    meta_description = models.TextField (blank=True, help_text="Meta description")
    meta_keywords    = models.TextField (blank=True, help_text="Meta keywords")

    published   = models.BooleanField (default=True)
    created     = models.DateTimeField (auto_now_add=True)
    updated     = models.DateTimeField (auto_now=True)

    objects     = PublishedManager()
    tags        = TaggableManager(blank=True)

    def __unicode__ (self):
        return self.name

    class Meta:
        db_table = u'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sortorder', 'name']

    def get_absolute_url (self):
        return self.url

    @property
    def url (self):
        return "/products/%s/" % self.slug

    @property
    def prods_as_list_divs (self):  # Used in category page (product list)
        if [True for p in Product.objects.published().filter (category=self) if not p.blurb]:
          # don't return any unless they're all present for this category - remove after migration - JJW 10/14/15
          return ''

        return mark_safe (
          '\n'.join ([p.as_list_div for p in Product.objects.published().filter (category=self)]) # .order_by('-sortorder')
        )

    def prods_as_lis (self):
        return mark_safe (TagStream22()
            .li (prod = Product.objects.filter (category=self, published=True))
                .a ('{prod.name}', href='{prod.url}', title='{prod.title_or_name}')
            .render()
        )

    def prods_as_divs (self):
        return mark_safe (TagStream22()
            .div (prod = Product.objects.filter (category=self, published=True), _class='product')
                .a ('{prod.name}', href='{prod.url}', title='{prod.title_or_name}')
            .render()
        )


class ChoiceCategory(models.Model):
    name = models.CharField(max_length=80)
    abbrev = models.CharField(max_length=10, blank=True, help_text= 'For prefixes on choice display names - typically 3 chars, uppercase')

    sohigh = models.IntegerField ("High Sort Order", default=0)  # blank=True,
    solow  = models.IntegerField ("Low Sort Order",  default=0)  # blank=True,

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    published   = models.BooleanField (default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects     = PublishedManager()

    #def __unicode__ (self):
    #  return '%s (%s)' % (self.name, self.abbrev)

    # could rename this to label
    def __unicode__ (self):
      s = self.abbrev or self.name
      if self.parent:
        s = u'%s:%s' % (self.parent, s)
      return s

    class Meta:
        verbose_name_plural = "Choice Categories"
        db_table = u'choicecategories'


#### Default required object

misc_choice_category_id = 43882

def get_misc_choice_category():
    try:
        return ChoiceCategory.objects.get(name='Misc').pk
    except:
        return misc_choice_category_id


class Option(models.Model):
    name        = models.CharField(max_length=50,       help_text='Option Name - shown in config grid unless overriden by ProdutOption name.')
    usage_notes = models.CharField(max_length=80, blank=True, help_text='Usage notes - used internally to disambiguate options with the same name.')
    sortorder   = models.IntegerField(                  help_text='Sort order for this option - The options appear ordered by this in the config grid.')
    #choices     = models.ManyToManyField (Choice, related_name='options', help_text='"OptionList" of Choices - NEW July 2011 for POOL architecture.')  # through='OptionList',
    choices     = models.ManyToManyField ("Choice", related_name='+', help_text='"OptionList" of Choices - NEW July 2011 for POOL architecture.')  # through='OptionList',
    blurb       = models.TextField (blank=True,         help_text='Short description, typically a few lines, HTML OK.')
    description = models.TextField (blank=True,         help_text='Detailed description, HTML OK.')
    #dependencies = models.CharField(max_length=50, help_text="Not used as of July 2011 - let's do something with this - JJW")
    #faq = models.TextField(Blank=True, help_text="Not used as of July 2011 - let's do something with this - JJW")
    comments    = models.TextField (blank=True,         help_text='Internal notes and comments.  Please add dates & your initials')

    published   = models.BooleanField (default=True)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    objects     = PublishedManager()

    def __unicode__ (self):
        #return smart_str(self.name)
        if self.usage_notes:
            return u'%s: %s (%s)' % (self.sortorder, self.name, self.usage_notes)
        else:
            return u'%s: %s' % (self.sortorder, self.name)

    class Meta:
        db_table = u'options'
        ordering = ['sortorder']


class Choice(models.Model):
    name        = models.CharField(max_length=80)
    #supplier   = models.IntegerField(blank=True, help_text="Primary supplier of this component") # someday an m2m to mfrs, distribs
    source      = models.CharField(max_length=80, blank=True)
    price       = models.FloatField(null=True, blank=True, help_text='Override cost-based calculated price with this (not used much)')
    cost        = models.FloatField(help_text='Our internal cost, used to calculate prices & differences')
    sortorder   = models.IntegerField()
    multiplier  = models.IntegerField(null=True, help_text='Override internal multiplier with this if >0 (not used much, can be 1 to sell at cost)')
    comment     = models.TextField(blank=True, null=True)
    choicecategory = models.ForeignKey("ChoiceCategory", verbose_name='category', default=get_misc_choice_category)
    blurb       = models.TextField(blank=True, help_text='Short description, typically a few lines, HTML OK.')
    # description? specs? features? esp when nested..
    #comments   = models.TextField (blank=True,         help_text='Internal notes and comments.  Please add dates & your initials')
    options     = models.ManyToManyField (Option, through=Option.choices.through, related_name='+')

    published   = models.BooleanField(default=True)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    objects     = PublishedManager()

    def __unicode__ (self):
        #return '%s ($ %0.2f)' % (smart_str(self.name), self.cost)  # , %s, %s]' % (smart_str(self.name), self.cost, self.price, self.multiplier)
        #return '%s ($%s)' % (smart_str(self.name), self.cost)  # , %s, %s]' % (smart_str(self.name), self.cost, self.price, self.multiplier)
        # JJW 4/24/14
        return '%s:%s ($%s)' % (self.choicecategory, smart_str(self.name), self.cost)  # , %s, %s]' % (smart_str(self.name), self.cost, self.price, self.multiplier)

    @property
    def calc_markup (self):
        if self.multiplier:
            return self.multiplier
        else:
            return 1.35  # Move to a "global settings" table or definition location

    @property
    def calc_price (self):
      if self.price:
          return self.price
      else:
          return self.cost * self.calc_markup

    #def calc_pricedelta (self, baseline):
    #    pass

    class Meta:
        db_table = u'choices'
        ordering = ['sortorder', 'cost']


#### Default required object

none_choice_id = 30

def get_none_choice():
    try:
        return Choice.objects.get(name='none').pk
    except:
        return none_choice_id



#### Product model

class ProductImage (Publishable, ImageBase):
    fk_name     = 'product'
    images_dir  = "images/products/"
    image       = FileBrowseField(max_length=200, directory = images_dir)
    product     = models.ForeignKey ('Product', related_name = 'images')

class Product (Imageable):
    name        = models.CharField(max_length=50,       help_text='Product name - by convention is "eRacks/<sku>".')  # should derive one of these
    sku         = models.CharField(unique=True, max_length=50, help_text="Our sku, also used as our Model Number or MPN (Manufacturer's Part Number).")
    baseprice   = models.FloatField(                    help_text='Base / baseline price for this model.')
    cost        = models.FloatField(                    help_text='Our cost - note that this field is not updated as our costs change, so is likely to be old.')
    category    = models.ForeignKey("Categories", db_column='categoryid', help_text='Legacy Zope Category for this product.')
    options     = models.ManyToManyField (Option, through='Prodopt', help_text='ProductOptions for this product - used by BOTH legacy Zope PO-POC architecture, and the new Django PO-OL architecture.')
    weight      = models.IntegerField(default=40,       help_text="Total shipping weight in lbs - defaults to 40.")  # required!
    baseoptions = models.CharField(max_length=254, blank=True)  # is this used? 2/12 JJW
    sortorder   = models.IntegerField(default=0)
    blurb       = models.TextField(blank=True,          help_text='Short description, typically a few lines, HTML OK.')
    description = models.TextField(blank=True,          help_text='Detailed description, HTML OK.')
    features    = models.TextField (blank=True,         help_text='Features, shown on Product Features tab.')  # old: which we split by line and display as bullets
    #specs       = models.TextField (blank=True,        help_text='Specifications, which we split by line and display as bullets.')
    comments    = models.TextField (blank=True,         help_text='Internal notes and comments.  Please add dates & your initials')
    link        = models.CharField(max_length=150, blank=True)  # is this used? 2/12 JJW
    title       = models.CharField(max_length=100, blank=True, help_text='If present, used for product page title (useful for SEO). Only for newer Django (non-Zope) products.')

    meta_title       = models.CharField (max_length=512, blank=True, help_text="Meta title")
    meta_description = models.TextField (blank=True, help_text="Meta description")
    meta_keywords    = models.TextField (blank=True, help_text="Meta keywords")

    meta_title       = models.CharField (max_length=512, blank=True, help_text="Meta title")
    meta_description = models.TextField (blank=True, help_text="Meta description")
    meta_keywords    = models.TextField (blank=True, help_text="Meta keywords")

    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    published   = models.BooleanField(default=True,     help_text='Filters whether product is shown in queries.')

    objects     = PublishedManager()
    tags        = TaggableManager(blank=True)

    def __unicode__ (self):
        return self.sku

    def get_absolute_url (self):
        return self.url # old: "/product/%s/" % self.sku

    @property
    def title_or_name (self):
        #print 'TITLE OR NAME', self.title or self.name
        return self.title or self.name

    @property
    def url (self):
        return "/products/%s/%s/" % (self.category.slug, self.sku)  # might want to slugify sku or add a slug field

    @property
    def slug (self):
        return slugify (self.sku)

    @property
    def image (self):
        imgs = self.images.published().order_by ('sortorder') [:1]
        if imgs: return imgs [0]

    @property
    def image_tag (self):
        imgs = self.images.published().order_by ('sortorder') [:1]
        return imgs [0].tag() if imgs else ''

    def product_options (self):
        return self.prodopt_set.order_by("option")

    @property
    def calc_description (self):
        if self.description:
            return self.description
        else:
            return '(No Description)'

    @property
    def calc_specs (self):
        if self.blurb:
            return self.blurb
        else:
            return '(No Specifications)'

    @property
    def as_list_div (self):  # For category page / product list - blurb, image, name
      return tags.div (
          tags.a (
              tags.div (self.image_tag, class_="primary-image") +
              tags.h3 (self.name),
            href="%s" % self.url) +
          tags.div (self.blurb, class_="product-blurb") +  # clearfix
          #tags.div ('Starting at ' +
          #    tags.a ('$%.f' % self.baseprice, class_="product-price", href="%s" % self.url),
          #  class_='product-price-line'),
          tags.a ('Starting at ' +
              tags.span ('$%.f' % self.baseprice, class_="product-price"),
            class_='product-price-line btn btn-success', href="%s" % self.url),
        class_='clearfix product-summary'
      )

    @property
    def prodopts_as_table (self):  # returns inner rows
        return ''.join ([po.as_rows for po in self.product_options()])

    class Meta:
        db_table = u'products'
        ordering = ['sortorder', 'sku']


#### Product - Option (Prodopt)  model

choice_orderby_choices = (
    ('cost','cost'),
    ('sortorder','sortorder'),
)

class Prodopt(models.Model):
    # 4 NEW fields SAT 7/9/11
    name = models.CharField(max_length=64, blank=True, help_text='Name to display in config grid - blank uses the Option name by default.')
    qty = models.IntegerField(default=1, help_text='The <b>Option Quantity</b> - the number of lines of this option to display in config grid. Defaults to 1.')
    single = models.BooleanField (default=False, help_text='If checked, there are no OptionChoices, the defaultchoice is the only possible choice.')
    required = models.BooleanField (default=False, help_text='If checked, this option will not have a "none" choice.  If false, a "none" choice will be available.')
    choices_orderby = models.CharField(max_length=20, choices=choice_orderby_choices, default='cost', help_text='Name to display in config grid - blank uses the Option name by default.')
    allowed_quantities = models.CommaSeparatedIntegerField (max_length=80, blank=True, default='', help_text="The allowed <b>Choice Quantities</b> - a comma-separated list of integers, eg '1,2,4' etc. Blank means don't display a quantity box.")

    product = models.ForeignKey(Product, db_column='productid')
    option = models.ForeignKey(Option, db_column='optionid')
    choices = models.ManyToManyField (Choice, through='Prodoptchoice', related_name='prodopts', blank=True, help_text='Legacy ProductOptionChoices - overrides OptionChoice list if present - Feb2012 JJW')
    defaultchoice = models.ForeignKey(Choice, default=get_none_choice, db_column='defaultchoiceid', help_text="Default choice from list of option-choices or legacy POCs - <b><span style='color:red'>SAVE TWICE to set this correctly</span></b>, otherwise fault will occur on ajax product update!")  # default='TBD',null=True, blank=True

    published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects     = PublishedManager()

    # these 4 from eRacks proto 7/10/11
    def calc_relative_price (self, ch):
      default_cost = self.defaultchoice.cost
      return spreadto5 (ch.cost, default_cost, ch.calc_markup)
      #default_price = self.defaultchoice.calc_price
      #return ch.calc_price - default_price

    def choice_name_and_price (self, ch):
      relative_price = self.calc_relative_price (ch)
      if relative_price:
        return '%s ($%.2f%s)' % (ch.name, relative_price, ' ea' if self.allowed_quantities else '')
      else:
        return '%s' % ch.name

    @property
    def calc_name (self):
      return self.name or self.option.name  # or self.option.display_name

    def option_choices (self):
        if self.single:
            #assert self.defaultchoice in self.option.choices.all()
            result = [self.defaultchoice.id]
        else:
            result = list (self.option.choices.order_by (self.choices_orderby).values_list ('id', flat=True))  # all()  #filter(published=True)],

        if not self.required:
            result.insert (0, none_choice_id)  # insert at front

        if self.required and none_choice_id in result:
            result.remove (none_choice_id)

        #return self.objects.in_bulk (result)  % this returns a dict indexed by the id - we need the query set:
        return Choice.objects.filter (id__in=result)

    def all_choices (self):
        if self.choices.count():
            return self.choices.all()
        else:
            return self.option_choices()

    def as_combos (self, lineid):
        if self.defaultchoice:
            selected = '%s,%s' % (lineid, self.defaultchoice.id)
        else:
            selected = None

        result = ''

        if self.allowed_quantities:
            result += tags.dropdown ([(q,'%s,%s' % (lineid, q)) for q in self.allowed_quantities.split(',')], name='choiceqty', cls='choiceqty')
            leaveroom = True
        else:
            leaveroom = False

        #result += TagStream().select (name='choiceid').option (value='(1,2)', 'hi there', selected = t/f

        result += tags.dropdown (
            #[(self.choice_name_and_price (c), (self.option.id,c.id)) for c in self.option_choices()],  #d='prodopt_%s' % self.option.id,  # self.name or self.option.name.replace(' ','_'),
            [(self.choice_name_and_price (c), '%s,%s' % (lineid, c.id)) for c in self.all_choices()],
                name='choiceid',  # self.name or self.option.name.replace(' ','_'),
                selected=selected,
                cls='choiceid' + (' leaveroom' if leaveroom else ''),
        )  # self.defaultchoice.id if self.defaultchoice else None)

        return result

    @property
    def as_rows (self):
        result = ''
        for i in range (self.qty):
            lineid = '%s_%s' % (self.id, i+1)
            result += (TagStream()
                .tr (d=lineid)
                    .td (self.calc_name, cls=lineid, title=self.option.blurb or self.calc_name + ' option')
                    .td (self.as_combos (lineid), cls=lineid + ' dropdowns')
                    .td (self.defaultchoice.name, cls='choiceinfo', title=self.defaultchoice.blurb or self.defaultchoice.name + ' (default choice)')
                    .td ('', cls='optprice')
                    #.td (self.option.blurb, d=self.defaultchoice.id)
                .render()
            )
        return result

        '''tags = self.qty * [TagStream()
            .tr (d=self.id)
                .td (self.calc_name, cls=self.id)
                .td (self.as_combos, cls=self.id)
                .td (self.defaultchoice.name, d=self.defaultchoice.id)
            .render()
        ]
        return tags'''


    def __unicode__ (self):
        return '%s: %s' % (self.product, self.option)

    #def save(self, *args, **kwargs):
    #    print 'IN SAVE'
    #    print self.defaultchoice
    #    super(Prodopt, self).save(*args, **kwargs) # Call the "real" save() method.

    class Meta:
        verbose_name = 'Product Option'
        db_table = u'prodopts'
        #ordering =


class Prodoptchoice(models.Model):
    #dt = models.DateTimeField() # auto_now=True)
    pricedelta = models.FloatField(null=True)  # default=0?
    productoption = models.ForeignKey(Prodopt, db_column='productoptionid') #, related_name='prodoptchoices')
    choice = models.ForeignKey('Choice', db_column='choiceid')
    current = models.CharField(null=True, max_length=1) # , default="T")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__ (self):
        return '%s: %s' % (self.productoption, self.choice)

    class Meta:
        verbose_name = 'Product-Option Choice'
        db_table = u'prodoptchoices'



#### Set up single-seq tables (org fm legacy eracks db - all db id's in one sequence)

from apps import helpers
from django.db.models.signals import pre_save

pre_save.connect (helpers.presave, sender=Product)
pre_save.connect (helpers.presave, sender=Prodopt)
pre_save.connect (helpers.presave, sender=Prodoptchoice)
pre_save.connect (helpers.presave, sender=Option)
pre_save.connect (helpers.presave, sender=Choice)
pre_save.connect (helpers.presave, sender=ChoiceCategory)
pre_save.connect (helpers.presave, sender=Categories)

#pre_save.connect (helpers.presave, sender=Image)

