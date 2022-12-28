from crawlers import CategoryCrawler, ProductCrawler, CommentStarCrawler
import time
import argparse



def main(args):
    if args.category:
        start = time.time()
        shopee_home_page = 'https://shopee.vn/'
        category = CategoryCrawler(home_page=shopee_home_page, headless_option=True)
        category.get_categories()
        # print(CategoryCrawler.categories_urls_dict)
        end = time.time()
        print("Finish in {} minutes".format((end - start) / 60))
    elif args.product:
        start = time.time()
        product = ProductCrawler(headless_option=True)
        product.get_products()
        end = time.time()
        print("Finish in {} minutes".format((end - start) / 60))
    elif args.comment:
        start = time.time()
        comment_star = CommentStarCrawler(headless_option=True)
        comment_star.get_stars_comments()
        end = time.time()
        print("Finish in {} minutes".format((end - start) / 60))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', action="store_true")
    parser.add_argument('--product', action="store_true")
    parser.add_argument('--comment', action="store_true")
    args = parser.parse_args()
    main(args)
